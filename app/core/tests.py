from django.test import TestCase
from unittest.mock import patch, MagicMock
from app.core.scraper import scrape_jobs, ScraperException
import os

class ScraperTests(TestCase):

    @patch('app.core.scraper.build')
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
            'items': [
                {
                    'title': 'Test Job 1',
                    'link': 'http://test.com/job1',
                    'pagemap': {'metatags': [{'og:site_name': 'Test Company 1'}]},
                    'snippet': 'Test description 1'
                },
                {
                    'title': 'Test Job 2',
                    'link': 'http://test.com/job2',
                    'pagemap': {'metatags': [{'og:site_name': 'Test Company 2'}]},
                    'snippet': 'Test description 2'
                }
            ]
        }
        mock_execute.return_value = mock_build

        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'CUSTOM_SEARCH_ENGINE_ID': 'test_id'}):
            jobs = scrape_jobs('test query', 'test.com')

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['title'], 'Test Job 1')
        self.assertEqual(jobs[1]['company'], 'Test Company 2')

    def test_scrape_jobs_missing_credentials(self):
        # Ensure that the environment variables are not set for this test
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ScraperException):
                scrape_jobs('test query', 'test.com')

    @patch('app.core.scraper.build')
    def test_scrape_jobs_api_error(self, mock_build):
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()

        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.side_effect = Exception("Google API Error")

        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'CUSTOM_SEARCH_ENGINE_ID': 'test_id'}):
            with self.assertRaises(Exception) as context:
                scrape_jobs('test query', 'test.com')
            self.assertEqual(str(context.exception), "Google API Error")
