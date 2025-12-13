from unittest.mock import patch

from backend.app import scraper


@patch("backend.app.scraper.FirestoreRepo")
@patch("backend.app.scraping_logic.scrape_and_save_jobs")
@patch("backend.app.scraper.db")  # Mock db to avoid real connection attempt
def test_handler(mock_db, mock_scrape, MockRepo):
    # Setup mocks
    mock_repo_instance = MockRepo.return_value
    mock_repo_instance.get_scrapable_domains.return_value = [
        {"id": "1", "domain": "example.com"}
    ]
    mock_scrape.return_value = 5

    # Run handler
    event = {}
    context = {}
    result = scraper.handler(event, context)

    # Assertions
    assert result["statusCode"] == 200
    assert "5 new jobs" in result["body"]
    mock_scrape.assert_called_once()
