import logging
from backend.app.firebase_config import db
from backend.app.firestore_repo import FirestoreRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_domains():
    repo = FirestoreRepo(db_client=db)
    domains = [
        "lever.co",
        "greenhouse.io",
        "ashbyhq.com",
        "workable.com"
    ]

    logger.info("Seeding domains...")
    for domain in domains:
        repo.add_scrapable_domain(domain)
        logger.info(f"Added/Verified domain: {domain}")
    logger.info("Domain seeding complete.")

if __name__ == "__main__":
    seed_domains()
