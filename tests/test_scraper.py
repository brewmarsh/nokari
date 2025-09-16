import unittest
from unittest.mock import patch, MagicMock
from app.core.scraper import scrape_jobs

from app.core.scraper import parse_job_title


class ScraperTestCase(unittest.TestCase):
    def test_parse_job_title(self):
        test_cases = {
            "Marketing Director, Rosetta Stone": {
                "cleaned_title": "Marketing Director",
                "company": "Rosetta Stone",
                "work_types": [],
            },
            "OpenX - Product Marketing Director": {
                "cleaned_title": "Product Marketing Director",
                "company": "OpenX",
                "work_types": [],
            },
            "Software Engineer - Remote": {
                "cleaned_title": "Software Engineer",
                "company": None,
                "work_types": ["remote"],
            },
            "Marketing Director, Rosetta Stone - Remote": {
                "cleaned_title": "Marketing Director",
                "company": "Rosetta Stone",
                "work_types": ["remote"],
            },
            "Manager, ": {
                "cleaned_title": "Manager",
                "company": None,
                "work_types": [],
            },
            "Job Application for Software Engineer": {
                "cleaned_title": "Software Engineer",
                "company": None,
                "work_types": [],
            },
            "Senior Analyst at ACME Corp": {
                "cleaned_title": "Senior Analyst",
                "company": "ACME Corp",
                "work_types": [],
            },
            "Lead Designer | Cool Startup": {
                "cleaned_title": "Lead Designer",
                "company": "Cool Startup",
                "work_types": [],
            },
            "Software Engineer": {
                "cleaned_title": "Software Engineer",
                "company": None,
                "work_types": [],
            },
            "Software Engineer, onsite": {
                "cleaned_title": "Software Engineer",
                "company": None,
                "work_types": ["onsite"],
            },
        }

        for title, expected in test_cases.items():
            with self.subTest(title=title):
                self.assertEqual(parse_job_title(title), expected)

    @patch("app.core.scraper.build")
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
            jobs = scrape_jobs(query="Software Engineer", domain="smartrecruiters.com")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "SmartRecruiters")


if __name__ == "__main__":
    unittest.main()
