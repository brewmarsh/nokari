from celery import shared_task
from .scraping_logic import scrape_and_save_jobs
from .models import ScrapableDomain

from django.contrib.auth import get_user_model
from .models import JobPosting, Resume
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_jobs_task(query):
    """
    A Celery task to scrape jobs in the background.
    """
    domains = ScrapableDomain.objects.all()
    scrape_and_save_jobs(query, domains)

def placeholder_match_resume(resume_text, job_description):
    """A placeholder function to simulate resume matching."""
    # In a real implementation, this would involve a proper NLP/ML model.
    # For now, it returns a mock score.
    return {'scores': [0.5]}

@shared_task
def analyze_resume_against_jobs(user_id):
    """
    Analyzes a user's resume against all job postings and updates the
    confidence scores.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        resume = Resume.objects.filter(user=user).latest('uploaded_at')
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found.")
        return
    except Resume.DoesNotExist:
        logger.info(f"No resume found for user {user_id} to analyze.")
        return

    try:
        with open(resume.file.path, 'r') as f:
            resume_text = f.read()
    except FileNotFoundError:
        logger.error(f"Resume file not found for user {user_id} at path {resume.file.path}")
        return

    job_postings = JobPosting.objects.all()
    updated_postings = []
    for job in job_postings:
        # Using the placeholder function for now
        score = placeholder_match_resume(resume_text, job.description)['scores'][0]
        job.confidence_score = score
        updated_postings.append(job)

    if updated_postings:
        JobPosting.objects.bulk_update(updated_postings, ['confidence_score'])
        logger.info(f"Updated confidence scores for {len(updated_postings)} jobs against resume of user {user_id}.")
