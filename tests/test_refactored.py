import unittest
from unittest.mock import patch, MagicMock
from app.core.scraping_logic import scrape_jobs


class RefactoredScraperTestCase(unittest.TestCase):
    @patch("app.core.scraping_logic.scrape_job_details")
    @patch("app.core.scraping_logic.build")
    def test_scrape_jobs_overrides_with_scraped_details(
        self, mock_build, mock_scrape_details
    ):
        """
        Tests that scrape_jobs correctly calls the detail scraper and overrides
        the initial data with the more accurate, scraped details.
        """
        # --- Setup Mocks ---

        # 1. Mock the Google Custom Search API client
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        # Simulate a Google API response with one job item
        mock_list.execute.return_value = {
            "items": [
                {
                    "title": "Initial Job Title",
                    "link": "https://example.com/job/123",
                    "snippet": "Initial snippet.",
                    "pagemap": {"metatags": [{"og:site_name": "Initial Company"}]},
                }
            ]
        }
        mock_cse.list.return_value = mock_list
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # 2. Mock the detail scraper function (scrape_job_details)
        # Simulate it returning more accurate details scraped from the job page
        mock_scrape_details.return_value = {
            "title": "Detailed Scraped Title",
            "description": "This is the full, detailed description from the website.",
        }

        # --- Test Execution ---

        # 3. Patch environment variables and call the function
        with patch.dict(
            "os.environ",
            {"GOOGLE_API_KEY": "fake_key", "CUSTOM_SEARCH_ENGINE_ID": "fake_id"},
        ):
            jobs = scrape_jobs(query="Software Engineer", domain="example.com")

        # --- Assertions ---

        # 4. Verify the results
        self.assertEqual(len(jobs), 1)
        job = jobs[0]

        # Check that the initial data was overridden by scrape_job_details
        self.assertEqual(job["title"], "Detailed Scraped Title")
        self.assertEqual(
            job["description"],
            "This is the full, detailed description from the website.",
        )

        # Check that data not returned by the detail scraper remains intact
        self.assertEqual(job["link"], "https://example.com/job/123")
        self.assertEqual(job["company"], "Initial Company")

        # 5. Verify that our mocks were called as expected
        mock_build.assert_called_once_with(
            "customsearch", "v1", developerKey="fake_key"
        )
        mock_scrape_details.assert_called_once_with("https://example.com/job/123")


if __name__ == "__main__":
    unittest.main()
