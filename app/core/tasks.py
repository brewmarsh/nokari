from celery import shared_task
from .scraping_logic import scrape_and_save_jobs
from .models import ScrapableDomain

@shared_task
def scrape_jobs_task(query):
    """
    A Celery task to scrape jobs in the background.
    """
    domains = ScrapableDomain.objects.all()
    scrape_and_save_jobs(query, domains)
