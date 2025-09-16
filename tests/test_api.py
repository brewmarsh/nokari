from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch
from app.core.models import JobPosting
import urllib.parse

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(  # nosec B106
            username="admin",
            email="admin@example.com",
            password="password",
            role="admin",
        )
        self.job_posting = JobPosting.objects.create(
            title="Software Engineer",
            link="https://jobs.lever.co/calstart/123",
            company="Calstart",
            description="A job.",
        )

    def test_rescrape_job_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)

        # Double URL-encode the link to handle multiple layers of decoding
        encoded_link = urllib.parse.quote(
            urllib.parse.quote(self.job_posting.link, safe=""), safe=""
        )

        url = f"/api/admin/jobs/{encoded_link}/rescrape/"

        with patch("app.core.views.rescrape_job_details_task.delay") as mock_task:
            response = self.client.post(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], "rescrape_task_started")
            mock_task.assert_called_once_with(self.job_posting.pk)
