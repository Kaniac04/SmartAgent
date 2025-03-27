from pysafebrowsing import SafeBrowsing
from urllib.parse import urlparse
import logging
from config.config import settings
from huggingface_hub import InferenceClient
from typing import List

hf_client = InferenceClient(token=settings.HF_API_TOKEN)

logger = logging.getLogger(__name__)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings using Hugging Face Inference API"""
    try:
        # The API accepts both single strings and lists of strings
        embeddings = hf_client.feature_extraction(
            texts,
            model=settings.EMBEDDING_MODEL,
            wait_for_model=True
        )
        return embeddings
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise


safe_browsing = SafeBrowsing(settings.GOOGLE_API_KEY)

def is_onion_domain(url: str) -> bool:
    """Check if URL is a .onion (Tor) domain"""
    parsed = urlparse(url)
    return parsed.netloc.endswith('.onion')

def contains_suspicious_keywords(url: str) -> bool:
    """Check for suspicious keywords in URL"""
    suspicious_keywords = [
        'xxx', 'porn', 'adult', 'nsfw', 'sex',
        'gambling', 'bet', 'casino',
        'hack', 'crack', 'warez', 'torrent',
        'drugs', 'darknet', 'blackmarket'
    ]
    
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in suspicious_keywords)

def is_url_safe(url: str) -> tuple[bool, str]:
    """
    Check if URL is safe to scrape
    Returns: (is_safe: bool, reason: str)
    """
    try:
        # Basic URL format validation
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False, "Invalid URL format"
        
        # Check for HTTPS
        if parsed.scheme != 'https':
            return False, "Only HTTPS URLs are allowed"
        
        # Check for .onion domains
        if is_onion_domain(url):
            return False, "Tor/Onion domains are not allowed"
            
        # Check for suspicious keywords
        if contains_suspicious_keywords(url):
            return False, "URL contains suspicious keywords"
            
        result = safe_browsing.lookup_urls([url])
        
        if result and url in result:
            url_result = result[url]
            if 'malicious' in url_result and url_result['malicious']:
                threats = url_result.get('threats', [])
                return False, f"URL flagged as unsafe: {', '.join(threats)}"
        
        return True, "URL is safe"
        
    except Exception as e:
        logger.error(f"URL safety check failed: {str(e)}")
        return False, f"Safety check failed: {str(e)}"