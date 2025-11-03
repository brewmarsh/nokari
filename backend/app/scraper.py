from datetime import datetime, timezone

from backend.app.dynamo_repo import DynamoRepo

# In a real application, this list would be fetched from a database or a config file.
SCRAPABLE_DOMAINS = ["example.com/jobs", "another-example.com/careers"]


def scrape_domain(domain: str):
    """
    A placeholder function to simulate scraping a domain for jobs.
    In a real implementation, this would involve making HTTP requests and parsing HTML.
    """
    print(f"Scraping {domain} for jobs...")
    # Simulate finding a few jobs
    return [
        {
            "title": f"Software Engineer at {domain.split('.')[0]}",
            "company": domain.split(".")[0],
            "location": "Remote",
            "description": "A scraped job opening.",
            "work_arrangement": "Remote",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "title": f"Product Manager at {domain.split('.')[0]}",
            "company": domain.split(".")[0],
            "location": "New York, NY",
            "description": "Another scraped job opening.",
            "work_arrangement": "Hybrid",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    ]


def handler(event, context):
    """
    The AWS Lambda handler for the daily job scraper.
    """
    dynamo_repo = DynamoRepo(table_name="NokariData")
    total_jobs_added = 0

    for domain in SCRAPABLE_DOMAINS:
        scraped_jobs = scrape_domain(domain)
        for job_data in scraped_jobs:
            # We'll use a combination of the company and title to create a unique ID
            # to help with idempotency. In a real scenario, we might use the job's URL.
            job_id = f"{job_data['company']}-{job_data['title']}".replace(
                " ", "-"
            ).lower()

            was_added = dynamo_repo.put_job_posting(job_id, job_data)
            if was_added:
                total_jobs_added += 1
                print(f"Added new job: {job_data['title']}")

    print(f"Scraping complete. Added {total_jobs_added} new jobs.")
    return {
        "statusCode": 200,
        "body": f"Successfully added {total_jobs_added} new jobs.",
    }
