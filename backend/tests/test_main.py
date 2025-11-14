import os
import json
import sys
import pytest
from unittest.mock import MagicMock, patch

# Set a dummy environment variable to satisfy the check in firebase_config.py
os.environ['FIREBASE_CREDENTIALS_JSON'] = json.dumps({
    "type": "service_account",
    "project_id": "dummy",
    "private_key_id": "dummy",
    "private_key": "dummy",
    "client_email": "dummy",
    "client_id": "dummy",
    "auth_uri": "dummy",
    "token_uri": "dummy",
    "auth_provider_x509_cert_url": "dummy",
    "client_x509_cert_url": "dummy"
})

# Mock the entire firebase_admin module to prevent it from trying to initialize.
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()
sys.modules['firebase_admin.storage'] = MagicMock()
sys.modules['firebase_admin.auth'] = MagicMock()

# Now it's safe to import the app
from backend.app.main import app  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

@pytest.fixture
def mock_get_current_user():
    with patch("backend.app.main.get_current_user", autospec=True) as mock_user:
        mock_user.return_value = {"email": "test@example.com"}
        yield mock_user

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
