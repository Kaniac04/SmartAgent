from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from services.mongo import collection,clean_collection
from services.qdrant import qdrant_client
import logging
from requests.exceptions import RequestException
from pymongo.errors import PyMongoError
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import VectorParams, Distance
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from config.config import settings
from services.utility import get_embeddings 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingStatus:
    def __init__(self):
        self._lock = Lock()
        self._is_scraping = False
        self._is_upserting = False
        self._completed = False
        self.current_message = "Waiting to start"

    def update(self, *, scraping=None, upserting=None, completed=None, message=None):
        with self._lock:
            if scraping is not None:
                self._is_scraping = scraping
            if upserting is not None:
                self._is_upserting = upserting
            if completed is not None:
                self._completed = completed
            if message is not None:
                self.current_message = message

    @property
    def is_completed(self):
        with self._lock:
            return self._completed and not (self._is_scraping or self._is_upserting)

# Initialize at module level
scraping_status = ScrapingStatus()

# Thread-safe sets with locks
class ThreadSafeSet:
    def __init__(self):
        self._set = set()
        self._lock = Lock()

    def add(self, item):
        with self._lock:
            self._set.add(item)

    def __contains__(self, item):
        with self._lock:
            return item in self._set

    def __len__(self):
        with self._lock:
            return len(self._set)

scraped_urls = ThreadSafeSet()
failed_urls = ThreadSafeSet()


def scrape_single_page(url, domain, session_id):
    if url in scraped_urls or url in failed_urls:
        return []
    
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        # logger.info(f"Validated: {url}")
        if not all([parsed_url.scheme, parsed_url.netloc]):
            logger.warning(f"Invalid URL format: {url}")
            failed_urls.add(url)
            return []

        # Get page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse content
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        text_content = "\n".join([p.get_text() for p in soup.find_all("p")])
        
        # Insert to MongoDB
        try:
            collection.insert_one({
                "url": url,
                "title": title,
                "content": text_content,
                "session_id": session_id
            })
            scraped_urls.add(url)
            logger.info(f"Successfully scraped: {url}")
        except PyMongoError as e:
            logger.error(f"MongoDB insertion failed for {url}: {str(e)}")
            failed_urls.add(url)
            return []

        # Collect links for next batch
        new_urls = []
        for link in soup.find_all("a", href=True):
            try:
                new_url = link["href"]
                parsed_new_url = urlparse(new_url)
                if parsed_new_url.netloc == "" or parsed_new_url.netloc == domain:
                    absolute_url = new_url if parsed_new_url.netloc else f"{parsed_url.scheme}://{domain}{new_url}"
                    new_urls.append(absolute_url)
            except Exception as e:
                logger.error(f"Error processing link {link}: {str(e)}")
                continue

        return new_urls

    except RequestException as e:
        logger.error(f"Request failed for {url}: {str(e)}")
        failed_urls.add(url)
        return []
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {str(e)}")
        failed_urls.add(url)
        return []

def start_scraping(url, session_id, max_workers=5, url_limit=100):
    
    create_qdrant_collection()
    clean_collection()

    try:
        scraping_status.update(scraping=True, message="Starting scraping process...")

        domain = urlparse(url).netloc
        urls_to_scrape = [url]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while urls_to_scrape and len(scraped_urls) < url_limit:
                # Submit batch of URLs to thread pool
                future_to_url = {
                    executor.submit(scrape_single_page, url, domain, session_id): url 
                    for url in urls_to_scrape[:url_limit - len(scraped_urls)] 
                    if url not in scraped_urls and url not in failed_urls
                }
                
                # Clear current batch
                urls_to_scrape = []
                
                # Collect results and new URLs
                for future in as_completed(future_to_url):
                    if len(scraped_urls) >= url_limit:
                        break
                    new_urls = future.result()
                    urls_to_scrape.extend(new_urls)
        
        logger.info(f"Scraping completed. Processed {len(scraped_urls)} URLs (limit: {url_limit})")
        
        if scraped_urls:
            scraping_status.update(scraping=False, upserting=True, message="Upserting to vector database...")
            upsert_to_qdrant()
            scraping_status.update(upserting=False, completed=True, message="Process completed successfully")
        
        return {
            "success": True,
            "scraped": len(scraped_urls),
            "failed": len(failed_urls),
            "limit_reached": len(scraped_urls) >= url_limit
        }
    except Exception as e:
        scraping_status.update(scraping=False, upserting=False, completed=True, message=f"Error: {str(e)}")
        logger.error(f"Scraping failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def upsert_to_qdrant(batch_size=5):
    try:
        data = list(collection.find({}, {"_id": 0}))
        if not data:
            logger.warning("No data found in MongoDB to upsert to Qdrant")
            return
        
        embeddings = []
        valid_data = []
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                batch_embeddings = get_embeddings([doc["content"] for doc in batch])
                embeddings.extend(batch_embeddings)
                valid_data.extend(batch)
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            except Exception as e:
                logger.error(f"Batch embedding failed: {str(e)}")
                continue
        
        if not embeddings:
            logger.warning("No valid embeddings generated")
            return
            
        total_points = len(valid_data)
        for i in range(0, total_points, batch_size):
            batch_end = min(i + batch_size, total_points)
            points_batch = [
                {"id": j, "vector": embeddings[j], "payload":{
                                                            **valid_data[j],
                                                            "session_id": valid_data[j]["session_id"]}}
                for j in range(i, batch_end)
            ]
            
            try:
                # Increase timeout for larger batches
                qdrant_client.upsert(
                    collection_name=settings.COLLECTION_NAME,
                    points=points_batch,
                    wait = True
                )
                logger.info(f"Successfully upserted batch {i//batch_size + 1} ({len(points_batch)} points)")
                scraping_status.update(message=f"Upserting batch {i//batch_size + 1} of {(total_points + batch_size - 1)//batch_size}")
            except UnexpectedResponse as e:
                logger.error(f"Batch {i//batch_size + 1} upsert failed: {str(e)}")
                continue
            
        logger.info(f"Completed upserting all {total_points} documents to Qdrant")
        
    except Exception as e:
        scraping_status.update(message=f"Upsertion error: {str(e)}")
        logger.error(f"Unexpected error during Qdrant upsert: {str(e)}")
        raise 

    except PyMongoError as e:
        logger.error(f"MongoDB error during Qdrant upsert: {str(e)}")
    except UnexpectedResponse as e:
        logger.error(f"Qdrant upsert failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during Qdrant upsert: {str(e)}")

def create_qdrant_collection():
    try:
        if qdrant_client.collection_exists(settings.COLLECTION_NAME):
            qdrant_client.delete_collection(settings.COLLECTION_NAME)
            
        qdrant_client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        logger.info("Qdrant collection created")
    except UnexpectedResponse as e:
        logger.error(f"Qdrant collection creation failed: {str(e)}")