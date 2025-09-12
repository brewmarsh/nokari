from django.core.management.base import BaseCommand
from app.core.models import JobPosting
from app.core.scraping_logic import scrape_job_details
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Backfills job details for existing job postings.'

    def handle(self, *args, **options):
        self.stdout.write('Starting backfill process for job details...')

        job_postings = JobPosting.objects.all()
        total_jobs = job_postings.count()
        updated_count = 0

        for i, job in enumerate(job_postings):
            self.stdout.write(f'Processing job {i + 1}/{total_jobs}: {job.link}')

            if not job.link:
                self.stdout.write(self.style.WARNING(f'Skipping job with no link: {job.title}'))
                continue

            details = scrape_job_details(job.link)

            if details:
                updated = False
                if details.get('title') and details['title'] != job.title:
                    job.title = details['title']
                    updated = True
                if details.get('description') and details['description'] != job.description:
                    job.description = details['description']
                    updated = True

                if updated:
                    job.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated job: {job.title}'))
                else:
                    self.stdout.write('No new details found to update.')
            else:
                self.stdout.write(self.style.WARNING(f'Could not scrape details for job: {job.title}'))

        self.stdout.write(self.style.SUCCESS(f'Backfill process complete. Updated {updated_count} of {total_jobs} jobs.'))
