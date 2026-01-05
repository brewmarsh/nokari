import logging
import time
from datetime import datetime, timezone
from backend.app.firestore_repo import FirestoreRepo
from backend.app.firebase_config import db
from backend.app import scraping_logic

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run_scraper(query: str = "Software Engineer"):
    repo = FirestoreRepo(db_client=db)
    domains = repo.get_scrapable_domains()

    if not domains:
        print("No scrapable domains found in database.")
        return 0

    print(f"Starting scrape for query: {query}")
    start_time = time.time()

    try:
        count = scraping_logic.scrape_and_save_jobs(repo, query, domains)
        status = "success"
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        status = "failed"
        count = 0

    end_time = time.time()
    duration = end_time - start_time

    # Record history
    history_entry = {
        "timestamp": datetime.now(timezone.utc),
        "status": status,
        "jobs_found": count,
        "duration_seconds": duration,
        "query": query,
    }
    repo.add_scrape_history_entry(history_entry)

    print(f"Scraping complete. Added {count} new jobs.")
    return count


def handler(event, context):
    """
    The AWS Lambda handler for the daily job scraper.
    """
    # Event might contain query?
    query = event.get("query", "Software Engineer")
    count = run_scraper(query)
    return {
        "statusCode": 200,
        "body": f"Successfully scraped {count} new jobs.",
    }
