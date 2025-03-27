from fastapi import APIRouter, BackgroundTasks, Form
from services.scraper import start_scraping, scraped_urls, failed_urls, scraping_status
from services.qdrant import qdrant_client
from services.utility import is_url_safe


router = APIRouter()

@router.post("/scrape")
async def scrape_url(background_tasks: BackgroundTasks, url: str = Form(...), session_id: str = Form(...)):
    try:

        is_safe, reason = is_url_safe(url)
        if not is_safe:
            return {
                "status": "error",
                "message": f"URL rejected: {reason}"
            }

        background_tasks.add_task(start_scraping, url, session_id)
        return {"status": "success", "message": "Scraping started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/scraping-status")
async def get_scraping_status():
    return {
        "status": "success",
        "message": scraping_status.current_message,
        "scraped": len(scraped_urls),
        "failed": len(failed_urls),
        "completed": scraping_status.is_completed
    }