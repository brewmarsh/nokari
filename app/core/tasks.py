from celery import shared_task
from .scraper import scrape_jobs, ScraperException
from .models import JobPosting, ScrapableDomain, ScrapeHistory, SearchableJobTitle
from django.utils import timezone

@shared_task
def scrape_and_save_jobs(domain_id):
    """
    A Celery task to scrape jobs from a given domain and save them to the database.
    """
    try:
        domain = ScrapableDomain.objects.get(id=domain_id)
        job_titles = domain.searchable_job_titles.all()
        if not job_titles:
            job_titles = [None] # Ensure at least one scrape attempt if no titles are specified

        total_jobs_found = 0
        total_jobs_added = 0
        errors = []

        for title_model in job_titles:
            query = title_model.title if title_model else "software engineer" # Default query
            try:
                scraped_jobs = scrape_jobs(query=query, domain=domain.domain)
                total_jobs_found += len(scraped_jobs)

                for job_data in scraped_jobs:
                    # Avoid creating duplicate jobs
                    if not JobPosting.objects.filter(link=job_data['link']).exists():
                        JobPosting.objects.create(
                            title=job_data['title'],
                            link=job_data['link'],
                            company=job_data['company'],
                            description=job_data['description'],
                            posting_date=job_data.get('posting_date'),
                            locations=job_data.get('locations', [])
                        )
                        total_jobs_added += 1

            except ScraperException as e:
                errors.append(str(e))
                continue # Continue to next title

        ScrapeHistory.objects.create(
            domain=domain,
            status='success' if not errors else 'partial_failure',
            jobs_found=total_jobs_found,
            new_jobs_added=total_jobs_added,
            notes=', '.join(errors) if errors else f"Successfully scraped {domain.domain}"
        )
        return f"Scraping finished for {domain.domain}. Found: {total_jobs_found}, Added: {total_jobs_added}."

    except ScrapableDomain.DoesNotExist:
        ScrapeHistory.objects.create(
            domain=None,
            status='failure',
            notes=f"ScrapableDomain with id={domain_id} not found."
        )
        return f"Error: ScrapableDomain with id={domain_id} not found."
    except Exception as e:
        ScrapeHistory.objects.create(
            domain=ScrapableDomain.objects.filter(id=domain_id).first(),
            status='failure',
            notes=str(e)
        )
        return f"An unexpected error occurred: {str(e)}"
