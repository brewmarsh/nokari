import logging
import time
from datetime import datetime, timezone
from backend.app.firestore_repo import FirestoreRepo
from backend.app.firebase_config import db
from backend.app import scraping_logic

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run_scraper(query: str = "Software Engineer", requested_by: str = "System"):
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
        "requested_by": requested_by,
    }
    repo.add_scrape_history_entry(history_entry)

    print(f"Scraping complete. Added {count} new jobs.")
    return count


def rescrape_all_jobs(requested_by: str = "System"):
    repo = FirestoreRepo(db_client=db)
    logger.info("Starting rescrape of all jobs")
    start_time = time.time()

    try:
        jobs = repo.get_all_jobs()
    except Exception as e:
        logger.error(f"Failed to fetch jobs for rescrape: {e}")
        return 0

    count = 0
    for job in jobs:
        link = job.get("link")
        job_id = job.get("id")
        if not link or not job_id:
            continue

        try:
            details = scraping_logic.scrape_job_details(link)
            if details:
                job.update(
                    {
                        "title": details.get("title") or job.get("title"),
                        "description": details.get("description")
                        or job.get("description"),
                        "updated_at": datetime.utcnow(),
                    }
                )
                repo.put_job_posting(job_id, job)
                count += 1
                logger.info(f"Rescraped job {job_id}")
            else:
                logger.warning(f"Failed to scrape details for job {job_id}")
        except Exception as e:
            logger.error(f"Error rescraping job {job_id}: {e}")

    end_time = time.time()
    duration = end_time - start_time

    logger.info(f"Rescrape complete. Updated {count} jobs in {duration} seconds.")
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
