from django.test import TestCase
from unittest.mock import patch, MagicMock
from app.core.scraper import scrape_jobs, ScraperException
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import JobPosting, UserJobInteraction, HiddenCompany, SearchableJobTitle, ScrapableDomain

User = get_user_model()


class HideJobPostingViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.job_posting = JobPosting.objects.create(
            link='http://example.com/job/1',
            title='Test Job',
            company='Test Company',
            description='Test Description'
        )
        self.client.force_authenticate(user=self.user)

    def test_hide_job_posting(self):
        """
        Ensure that a user can hide a job posting.
        """
        url = reverse('hide_job_posting')
        data = {'job_posting_link': self.job_posting.link}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            UserJobInteraction.objects.filter(
                user=self.user,
                job_posting=self.job_posting,
                hidden=True
            ).exists()
        )

    def test_get_job_postings_excludes_hidden(self):
        """
        Ensure that hidden job postings are not included in the list of job postings.
        """
        UserJobInteraction.objects.create(
            user=self.user,
            job_posting=self.job_posting,
            hidden=True
        )
        url = reverse('job_postings')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class HideCompanyViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.company_name = 'Test Company'
        self.job_posting = JobPosting.objects.create(
            link='http://example.com/job/1',
            title='Test Job',
            company=self.company_name,
            description='Test Description'
        )

    def test_hide_company(self):
        """
        Ensure that a user can hide a company.
        """
        url = reverse('hide_company')
        data = {'name': self.company_name}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            HiddenCompany.objects.filter(
                user=self.user,
                name=self.company_name
            ).exists()
        )

    def test_get_job_postings_excludes_hidden_company(self):
        """
        Ensure that job postings from hidden companies are not included in the list of job postings.
        """
        HiddenCompany.objects.create(user=self.user, name=self.company_name)
        url = reverse('job_postings')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class PinJobPostingViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.job_posting1 = JobPosting.objects.create(
            link='http://example.com/job/1',
            title='Test Job 1',
            company='Test Company',
            description='Test Description'
        )
        self.job_posting2 = JobPosting.objects.create(
            link='http://example.com/job/2',
            title='Test Job 2',
            company='Test Company',
            description='Test Description'
        )

    def test_pin_job_posting(self):
        """
        Ensure that a user can pin a job posting.
        """
        url = reverse('pin_job_posting')
        data = {'job_posting_link': self.job_posting1.link, 'pinned': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            UserJobInteraction.objects.get(
                user=self.user,
                job_posting=self.job_posting1
            ).pinned
        )

    def test_unpin_job_posting(self):
        """
        Ensure that a user can unpin a job posting.
        """
        UserJobInteraction.objects.create(user=self.user, job_posting=self.job_posting1, pinned=True)
        url = reverse('pin_job_posting')
        data = {'job_posting_link': self.job_posting1.link, 'pinned': False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            UserJobInteraction.objects.get(
                user=self.user,
                job_posting=self.job_posting1
            ).pinned
        )

    def test_get_job_postings_orders_by_pinned(self):
        """
        Ensure that job postings are ordered by pinned status.
        """
        UserJobInteraction.objects.create(user=self.user, job_posting=self.job_posting2, pinned=True)
        url = reverse('job_postings')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['link'], self.job_posting2.link)
        self.assertEqual(response.data[1]['link'], self.job_posting1.link)


class SearchableJobTitleViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='password')
        self.user = User.objects.create_user(email='user@example.com', password='password')
        self.job_title1 = SearchableJobTitle.objects.create(title='Software Engineer')
        self.job_title2 = SearchableJobTitle.objects.create(title='Product Manager')
        ScrapableDomain.objects.create(domain='example.com')

    def test_list_job_titles_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('job_title-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_job_titles_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('job_title-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_job_title_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('job_title-list')
        data = {'title': 'Data Scientist'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SearchableJobTitle.objects.count(), 3)

    def test_delete_job_title_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('job_title-detail', kwargs={'pk': self.job_title1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SearchableJobTitle.objects.count(), 1)

    @patch('app.core.views.scrape_jobs')
    def test_scrape_view_uses_job_titles(self, mock_scrape_jobs):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('scrape')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_scrape_jobs.assert_called()
        expected_query = '("Software Engineer" OR "Product Manager") AND "remote"'
        self.assertEqual(mock_scrape_jobs.call_args[0][0], expected_query)



class ScraperTests(TestCase):

    @patch("app.core.scraper.build")
    def test_scrape_jobs_success(self, mock_build):
        # Setup mock for Google API
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "title": "Test Job 1",
                    "link": "http://test.com/job1",
                    "pagemap": {"metatags": [{"og:site_name": "Test Company 1"}]},
                    "snippet": "Test description 1",
                },
                {
                    "title": "Test Job 2",
                    "link": "http://test.com/job2",
                    "pagemap": {"metatags": [{"og:site_name": "Test Company 2"}]},
                    "snippet": "Test description 2",
                },
            ]
        }
        mock_execute.return_value = mock_build

        with patch.dict(
            os.environ,
            {
                "GOOGLE_API_KEY": "test_key",
                "CUSTOM_SEARCH_ENGINE_ID": "test_id",
            },
        ):
            jobs = scrape_jobs("test query", "test.com")

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "Test Job 1")
        self.assertEqual(jobs[1]["company"], "Test Company 2")

    def test_scrape_jobs_missing_credentials(self):
        # Ensure that the environment variables are not set for this test
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ScraperException):
                scrape_jobs("test query", "test.com")

    @patch("app.core.scraper.build")
    def test_scrape_jobs_api_error(self, mock_build):
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()

        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.side_effect = Exception("Google API Error")

        with patch.dict(
            os.environ,
            {
                "GOOGLE_API_KEY": "test_key",
                "CUSTOM_SEARCH_ENGINE_ID": "test_id",
            },
        ):
            with self.assertRaises(Exception) as context:
                scrape_jobs("test query", "test.com")
            self.assertEqual(str(context.exception), "Google API Error")


class FindSimilarJobsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        ScrapableDomain.objects.create(domain='example.com')

    @patch('app.core.views.scrape_in_background')
    @patch('app.core.views.generate_embedding')
    def test_find_similar_jobs_triggers_scraping(self, mock_generate_embedding, mock_scrape_in_background):
        """
        Ensure the find-similar-jobs endpoint triggers a new scrape and returns similar jobs.
        """
        # Mock the embedding generation for any new job
        mock_generate_embedding.return_value = [0.5, 0.5, 0.5]

        # Existing jobs in the database
        target_job = JobPosting.objects.create(
            link='http://example.com/job/1',
            title='Senior Software Engineer',
            company='Tech Corp',
            description='Develop and maintain web applications using Python and Django.',
            embedding=[1.0, 0.0, 0.0]
        )
        # This job is already in the DB and is similar
        existing_similar_job = JobPosting.objects.create(
            link='http://example.com/job/2',
            title='Software Engineer',
            company='Innovate LLC',
            description='Experience with Python and Django is a plus.',
            embedding=[0.9, 0.1, 0.0]
        )
        # This job is not similar
        dissimilar_job = JobPosting.objects.create(
            link='http://example.com/job/3',
            title='Product Manager',
            company='Business Inc.',
            description='Define product strategy and roadmap.',
            embedding=[0.0, 1.0, 0.0]
        )

        url = reverse('find_similar_jobs', kwargs={'pk': target_job.link})
        response = self.client.post(url, format='json')

        # 1. Assert that the background scraper was called correctly
        mock_scrape_in_background.assert_called_once()
        expected_query = f'"{target_job.title}"'
        self.assertEqual(mock_scrape_in_background.call_args[0][0], expected_query)

        # 2. Assert that the response contains the correct jobs
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_links = {job['link'] for job in response.data}

        # It should contain the existing similar job
        self.assertIn(existing_similar_job.link, response_links)
        # It should NOT contain the dissimilar job
        self.assertNotIn(dissimilar_job.link, response_links)
