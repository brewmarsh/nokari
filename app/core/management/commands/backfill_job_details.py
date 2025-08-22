from django.core.management.base import BaseCommand
from django.utils import timezone
from app.core.models import JobPosting
from app.core.scraper import scrape_job_details, ScraperException

class Command(BaseCommand):
    help = 'Backfills job details for existing job postings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting backfill process...'))

        job_postings = JobPosting.objects.filter(details_updated_at__isnull=True)
        updated_count = 0
        deleted_count = 0
        error_count = 0

        for job in job_postings:
            try:
                self.stdout.write(f'Processing job: {job.link}')
                description = scrape_job_details(job.link)
                job.description = description
                job.details_updated_at = timezone.now()
                job.save()
                updated_count += 1
            except ScraperException as e:
                if "URL not found (404)" in str(e):
                    self.stdout.write(self.style.WARNING(f'Job not found (404), deleting: {job.link}'))
                    job.delete()
                    deleted_count += 1
                else:
                    self.stderr.write(self.style.ERROR(f'Error processing job {job.link}: {e}'))
                    error_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'An unexpected error occurred for job {job.link}: {e}'))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Backfill process finished. '
            f'Updated: {updated_count}, Deleted: {deleted_count}, Errors: {error_count}'
        ))
