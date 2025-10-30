import unittest
from unittest.mock import MagicMock, patch

from app.core.scraping_logic import scrape_jobs


class ScraperTestCase(unittest.TestCase):
    @patch("app.core.scraping_logic.build")
    def test_scrape_jobs_company_name(self, mock_build):
        # Mock the Google Custom Search API response
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {
            "items": [
                {
                    "title": "Software Engineer",
                    "link": "https://jobs.smartrecruiters.com/some-company/123-software-engineer",
                    "snippet": "A great job.",
                    "pagemap": {
                        "cse_thumbnail": [{"src": "https://example.com/logo.png"}],
                        "metatags": [{"og:site_name": "SmartRecruiters"}],
                    },
                }
            ]
        }
        mock_cse.list.return_value = mock_list
        mock_service.cse.return_value = mock_cse
        mock_build.return_value = mock_service

        # Set environment variables for the test
        with patch.dict(
            "os.environ",
            {"GOOGLE_API_KEY": "test_key", "CUSTOM_SEARCH_ENGINE_ID": "test_id"},
        ):
            with patch(
                "app.core.scraping_logic.scrape_job_details"
            ) as mock_scrape_details:
                mock_scrape_details.return_value = None
                jobs = scrape_jobs(
                    query="Software Engineer", domain="smartrecruiters.com"
                )

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "SmartRecruiters")


if __name__ == "__main__":
    unittest.main()
