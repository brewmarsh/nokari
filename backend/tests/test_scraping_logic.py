from unittest.mock import MagicMock, patch

from backend.app import scraping_logic
from backend.app.scraping_logic import scrape_job_details


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
                "locations": [{"type": "remote"}, {"location_string": "NY"}],
                "posting_date": None,
            }
        ]

        domains = [{"domain": "domain.com"}]
        count = scraping_logic.scrape_and_save_jobs(repo, "query", domains)

        assert count == 1
        repo.put_job_posting.assert_called_once()
        args, _ = repo.put_job_posting.call_args
        saved_job = args[1]
        assert "searchable_locations" in saved_job
        assert "remote" in saved_job["searchable_locations"]
        assert "NY" in saved_job["searchable_locations"]

class TestScrapingLogic:

    @patch('backend.app.scraping_logic.requests.get')
    def test_scrape_job_details_with_icims_iframe(self, mock_get):
        # Mock responses
        initial_response = MagicMock()
        initial_response.content = b'''
        <html>
            <head><title>Initial Page</title></head>
            <body>
                <iframe id="icims_content_iframe" src="iframe_content.html"></iframe>
            </body>
        </html>
        '''
        initial_response.raise_for_status.return_value = None

        iframe_response = MagicMock()
        iframe_response.content = b'''
        <html>
            <head><title>Iframe Page</title></head>
            <body>
                <div class="job-container">
                    <div class="header">
                        <span class="job-locations-label">Job Locations</span>
                        <span class="job-locations-value">DE-Berlin</span>
                    </div>
                    <div class="description">
                        This is the job description.
                    </div>
                </div>
            </body>
        </html>
        '''
        iframe_response.raise_for_status.return_value = None

        # Configure side_effect to return different responses based on URL
        def side_effect(url, timeout=10):
            if "iframe_content.html" in url:
                return iframe_response
            return initial_response

        mock_get.side_effect = side_effect

        details = scrape_job_details("http://example.com/job")

        assert details is not None
        assert details['title'] == "Iframe Page"
        assert "locations" in details
        assert len(details['locations']) == 1
        assert details['locations'][0]['location_string'] == "DE-Berlin"
        assert details['locations'][0]['type'] == "onsite"
        assert "This is the job description." in details['description']

    @patch('backend.app.scraping_logic.requests.get')
    def test_scrape_job_details_plain_text_location(self, mock_get):
        response = MagicMock()
        response.content = b'''
        <html>
            <head><title>Job Page</title></head>
            <body>
                <p>Job Locations US-Remote</p>
                <p>Description here.</p>
            </body>
        </html>
        '''
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        details = scrape_job_details("http://example.com/job")

        assert details is not None
        assert details['title'] == "Job Page"
        assert "locations" in details
        assert details['locations'][0]['location_string'] == "US-Remote"

    @patch('backend.app.scraping_logic.requests.get')
    def test_scrape_job_details_no_location(self, mock_get):
        response = MagicMock()
        response.content = b'''
        <html>
            <head><title>Job Page</title></head>
            <body>
                <p>Description here.</p>
            </body>
        </html>
        '''
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        details = scrape_job_details("http://example.com/job")

        assert details is not None
        assert "locations" not in details
