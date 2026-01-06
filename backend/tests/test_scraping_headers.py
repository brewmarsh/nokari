import unittest
from unittest.mock import patch, MagicMock
from backend.app.scraping_logic import scrape_job_details, get_session

class TestScrapingLogic(unittest.TestCase):

    def test_get_session_headers(self):
        session = get_session()
        self.assertIn("User-Agent", session.headers)
        self.assertIn("Accept-Language", session.headers)
        self.assertIn("Mozilla", session.headers["User-Agent"])

    @patch("backend.app.scraping_logic.requests.Session")
    def test_scrape_job_details_uses_session(self, mock_session_cls):
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.content = b"<html><title>Test Job</title></html>"
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        url = "https://example.com/job/1"
        result = scrape_job_details(url)

        mock_session.get.assert_called_with(url, timeout=10)
        self.assertEqual(result["title"], "Test Job")
        # Ensure headers were set (implied by using get_session inside)

    @patch("backend.app.scraping_logic.requests.Session")
    def test_scrape_job_details_follows_iframe(self, mock_session_cls):
        mock_session = mock_session_cls.return_value

        # First response has iframe
        mock_response_1 = MagicMock()
        mock_response_1.content = b'<html><iframe id="icims_content_iframe" src="/iframe_content"></iframe></html>'
        mock_response_1.status_code = 200

        # Second response (iframe content)
        mock_response_2 = MagicMock()
        mock_response_2.content = b'<html><title>Iframe Job Title</title></html>'
        mock_response_2.status_code = 200

        mock_session.get.side_effect = [mock_response_1, mock_response_2]

        url = "https://example.com/job/1"
        result = scrape_job_details(url)

        self.assertEqual(mock_session.get.call_count, 2)
        args, _ = mock_session.get.call_args_list[1]
        self.assertEqual(args[0], "https://example.com/iframe_content")
        self.assertEqual(result["title"], "Iframe Job Title")

if __name__ == "__main__":
    unittest.main()
