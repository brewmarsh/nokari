import logging
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
    count = scraping_logic.scrape_and_save_jobs(repo, query, domains)
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
