from celery import shared_task
from .scraper import scrape_jobs, ScraperException, scrape_job_details
from .models import JobPosting, ScrapableDomain, ScrapeHistory, SearchableJobTitle
from django.utils import timezone

@shared_task
def scrape_and_save_jobs(domain_id):
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
        except ScraperException as e:
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
    except ScraperException as e:
        if "404" in str(e):
            job.delete()
            return f"Job not found (404), deleted: {job.link}"
        else:
            return f"Error rescraping job {job.link}: {e}"
    except Exception as e:
        return f"An unexpected error occurred for job {job.link}: {e}"
