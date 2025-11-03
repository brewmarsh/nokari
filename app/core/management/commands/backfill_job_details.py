import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.core.models import JobPosting
from app.core.scraping_logic import scrape_job_details

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfills job details for existing job postings."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting backfill process..."))

        job_postings = JobPosting.objects.filter(details_updated_at__isnull=True)
        total_jobs = job_postings.count()
        updated_count = 0
        deleted_count = 0
        error_count = 0

        self.stdout.write(f"Found {total_jobs} jobs to process.")

        for i, job in enumerate(job_postings):
            self.stdout.write(f"Processing job {i + 1}/{total_jobs}: {job.link}")

            if not job.link:
                self.stdout.write(
                    self.style.WARNING(f"Skipping job with no link: {job.title}")
                )
                continue

            try:
                details = scrape_job_details(job.link)

                if details:
                    # Update description if it's different
                    if (
                        details.get("description")
                        and details["description"] != job.description
                    ):
                        job.description = details["description"]
                        job.details_updated_at = timezone.now()
                        job.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully updated description for job: {job.link}"
                            )
                        )
                    else:
                        self.stdout.write("No new details found to update.")

            except Exception as e:
                if "404" in str(e):
                    self.stdout.write(
                        self.style.WARNING(f"Job not found (404), deleting: {job.link}")
                    )
                    job.delete()
                    deleted_count += 1
                else:
                    self.stderr.write(
                        self.style.ERROR(
                            f"An unexpected error occurred for job {job.link}: {e}"
                        )
                    )
                    error_count += 1

        summary_message = (
            "Backfill process finished. "
            f"Updated: {updated_count}, Deleted: {deleted_count}, "
            f"Errors: {error_count}"
        )
        self.stdout.write(self.style.SUCCESS(summary_message))
