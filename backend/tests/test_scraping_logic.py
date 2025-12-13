from unittest.mock import MagicMock, patch

from backend.app import scraping_logic


@patch("backend.app.scraping_logic.build")
@patch("backend.app.scraping_logic.scrape_job_details")
def test_scrape_jobs(mock_details, mock_build):
    # Mock Google API
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.cse().list().execute.return_value = {
        "items": [
            {
                "title": "Software Engineer",
                "link": "http://example.com/job",
                "snippet": "Job description",
                "pagemap": {"metatags": [{"og:site_name": "Example Corp"}]},
            }
        ]
    }

    # Mock details
    mock_details.return_value = {"title": "Better Title", "description": "Better Desc"}

    # Set env vars
    with patch.dict(
        "os.environ", {"GOOGLE_API_KEY": "key", "CUSTOM_SEARCH_ENGINE_ID": "id"}
    ):
        jobs = scraping_logic.scrape_jobs("query", "domain.com")

    assert len(jobs) == 1
    assert jobs[0]["title"] == "Better Title"
    assert jobs[0]["company"] == "Example Corp"


def test_scrape_and_save_jobs():
    repo = MagicMock()
    repo.get_job_posting.return_value = None  # Job does not exist

    # Mock scrape_jobs to return one job
    with patch("backend.app.scraping_logic.scrape_jobs") as mock_scrape:
        mock_scrape.return_value = [
            {
                "title": "Job 1",
                "company": "Comp",
                "description": "Desc",
                "link": "http://link.com",
                "locations": [],
                "posting_date": None,
            }
        ]

        domains = [{"domain": "domain.com"}]
        count = scraping_logic.scrape_and_save_jobs(repo, "query", domains)

        assert count == 1
        repo.put_job_posting.assert_called_once()
