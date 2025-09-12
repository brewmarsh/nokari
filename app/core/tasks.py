from celery import shared_task
from .models import JobPosting, ScrapableDomain, ScrapeHistory, SearchableJobTitle, Resume
from .scraping_logic import scrape_jobs
from .scraping_logic import scrape_job_details
from .scraping_logic import parse_job_title
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_and_save_jobs_task(domain_id):
    """
    A Celery task to scrape jobs from a given domain and save them to the database.
    """
    try:
        domain = ScrapableDomain.objects.get(id=domain_id)
        job_titles = SearchableJobTitle.objects.all()
        if not job_titles:
            details = f"No searchable job titles found. Skipping scrape for {domain.domain}."
            ScrapeHistory.objects.create(status='success', details=details)
            return details

        total_jobs_found = 0
        total_jobs_added = 0
        errors = []

        query_parts = [f'"{title.title}"' for title in job_titles]
        query = f'({" OR ".join(query_parts)})'

        try:
            scraped_jobs = scrape_jobs(query=query, domain=domain.domain)
            total_jobs_found += len(scraped_jobs)

            for job_data in scraped_jobs:
                obj, created = JobPosting.objects.get_or_create(
                    link=job_data['link'],
                    defaults={
                        'title': job_data['title'],
                        'company': job_data['company'],
                        'description': job_data['description'],
                        'posting_date': job_data.get('posting_date'),
                        'locations': job_data.get('locations', [])
                    }
                )
                if created:
                    total_jobs_added += 1
        except Exception as e:
            errors.append(str(e))

        details = f"Scraped {domain.domain}. Found: {total_jobs_found}, Added: {total_jobs_added}."
        if errors:
            details += f" Errors: {', '.join(errors)}"
        ScrapeHistory.objects.create(
            status='success' if not errors else 'partial_failure',
            jobs_found=total_jobs_found,
            details=details
        )
        return f"Scraping finished for {domain.domain}. Found: {total_jobs_found}, Added: {total_jobs_added}."

    except ScrapableDomain.DoesNotExist:
        ScrapeHistory.objects.create(
            status='failure',
            details=f"ScrapableDomain with id={domain_id} not found."
        )
        return f"Error: ScrapableDomain with id={domain_id} not found."
    except Exception as e:
        ScrapeHistory.objects.create(
            status='failure',
            details=str(e)
        )
        return f"An unexpected error occurred: {str(e)}"

@shared_task
def backfill_job_titles_task():
    """
    Goes through all existing job postings and applies the new title parsing logic
    to backfill company and work type information.
    """
    total_jobs = JobPosting.objects.count()
    updated_count = 0

    for job in JobPosting.objects.all():
        parsed_data = parse_job_title(job.title)

        cleaned_title = parsed_data['cleaned_title']
        extracted_company = parsed_data['company']
        extracted_work_types = parsed_data['work_types']

        updated = False

        if job.title != cleaned_title:
            job.title = cleaned_title
            updated = True

        if (not job.company or job.company.startswith('http')) and extracted_company:
            job.company = extracted_company
            updated = True

        if job.locations is None:
            job.locations = []

        existing_work_types = {loc.get('type') for loc in job.locations if isinstance(loc, dict)}
        for work_type in extracted_work_types:
            if work_type not in existing_work_types:
                job.locations.append({'type': work_type})
                updated = True

        if updated:
            job.save()
            updated_count += 1

    return f"Backfill complete. Processed {total_jobs} jobs. Updated {updated_count} jobs."


@shared_task
def rescrape_job_details_task(job_posting_pk):
    """
    A Celery task to rescrape the details of a single job posting.
    """
    try:
        job = JobPosting.objects.get(pk=job_posting_pk)
    except JobPosting.DoesNotExist:
        return f"Job posting with pk={job_posting_pk} not found."

    try:
        description = scrape_job_details(job.link)
        job.description = description
        job.details_updated_at = timezone.now()
        job.save()
        return f"Successfully rescraped job: {job.link}"
    except Exception as e:
        return f"An unexpected error occurred for job {job.link}: {e}"

def placeholder_match_resume(resume_text, job_description):
    """A placeholder function to simulate resume matching."""
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
        score = placeholder_match_resume(resume_text, job.description)['scores'][0]
        job.confidence_score = score
        updated_postings.append(job)

    if updated_postings:
        JobPosting.objects.bulk_update(updated_postings, ['confidence_score'])
        logger.info(f"Updated confidence scores for {len(updated_postings)} jobs against resume of user {user_id}.")
