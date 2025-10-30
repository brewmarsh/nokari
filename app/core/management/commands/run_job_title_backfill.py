from django.core.management.base import BaseCommand

from app.core.tasks import backfill_job_titles_task


class Command(BaseCommand):
    help = (
        "Triggers a Celery task to backfill job titles with parsed data."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Queueing job title backfill task...")
        )
        backfill_job_titles_task.delay()
        self.stdout.write(
            self.style.SUCCESS(
                "Task queued. See Celery worker for progress."
            )
        )
