from backend.app import scraper
from unittest.mock import patch
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))


@patch("backend.app.scraper.DynamoRepo")
def test_scraper_handler(MockDynamoRepo):
    mock_repo_instance = MockDynamoRepo.return_value
    mock_repo_instance.put_job_posting.return_value = True  # Simulate all jobs are new

    event = {}
    context = {}

    result = scraper.handler(event, context)

    assert result["statusCode"] == 200
    assert "Successfully added" in result["body"]
    # Total jobs = 2 jobs per domain * 2 domains = 4
    assert mock_repo_instance.put_job_posting.call_count == 4
