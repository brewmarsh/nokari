from django.test import TestCase
from app.core.models import JobPosting
from app.core.tasks import backfill_job_titles_task

class TaskTestCase(TestCase):
    def test_backfill_job_titles_task(self):
        # Case 1: Title with company, no company set on object
        JobPosting.objects.create(
            title="Software Engineer at ACME Inc",
            link="http://example.com/1",
            company="",
            description="A job.",
        )

        # Case 2: Title with work type, locations is empty
        JobPosting.objects.create(
            title="Manager - Remote",
            link="http://example.com/2",
            company="Some Company",
            description="Another job.",
            locations=[],
        )

        # Case 3: Clean title, should not be changed
        JobPosting.objects.create(
            title="Product Designer",
            link="http://example.com/3",
            company="Another Company",
            description="Yet another job.",
        )

        # Case 4: Company is a URL, should be updated
        JobPosting.objects.create(
            title="Analyst, RealCorp",
            link="http://example.com/4",
            company="http://example.com/logo.png",
            description="A fourth job.",
        )

        # Run the backfill task
        result = backfill_job_titles_task()

        self.assertEqual(result, "Backfill complete. Processed 4 jobs. Updated 3 jobs.")

        # Verify Case 1
        job1 = JobPosting.objects.get(link="http://example.com/1")
        self.assertEqual(job1.title, "Software Engineer")
        self.assertEqual(job1.company, "ACME Inc")

        # Verify Case 2
        job2 = JobPosting.objects.get(link="http://example.com/2")
        self.assertEqual(job2.title, "Manager")
        self.assertEqual(job2.company, "Some Company") # Should not change
        self.assertIn({'type': 'remote'}, job2.locations)

        # Verify Case 3
        job3 = JobPosting.objects.get(link="http://example.com/3")
        self.assertEqual(job3.title, "Product Designer")
        self.assertEqual(job3.company, "Another Company")

        # Verify Case 4
        job4 = JobPosting.objects.get(link="http://example.com/4")
        self.assertEqual(job4.title, "Analyst")
        self.assertEqual(job4.company, "RealCorp")
