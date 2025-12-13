import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Set a dummy environment variable to satisfy the check in firebase_config.py
os.environ["FIREBASE_CREDENTIALS_JSON"] = json.dumps(
    {
        "type": "service_account",
        "project_id": "dummy",
        "private_key_id": "dummy",
        "private_key": "dummy",
        "client_email": "dummy",
        "client_id": "dummy",
        "auth_uri": "dummy",
        "token_uri": "dummy",
        "auth_provider_x509_cert_url": "dummy",
        "client_x509_cert_url": "dummy",
    }
)

# Mock the entire firebase_admin module
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.storage"] = MagicMock()
sys.modules["firebase_admin.auth"] = MagicMock()

# Import app after mocking
from backend.app.main import app  # noqa: E402
from backend.app.security import get_current_user  # noqa: E402


@pytest.mark.asyncio
async def test_add_scrapable_domain_as_admin():
    app.dependency_overrides[get_current_user] = lambda: {"uid": "admin-uid"}

    with (
        patch("backend.app.main.firestore_repo.get_user") as mock_db_user,
        patch("backend.app.main.firestore_repo.add_scrapable_domain") as mock_add,
    ):
        mock_db_user.return_value = {"role": "admin"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/scrapable-domains", json={"domain": "test.com"}
            )

    app.dependency_overrides = {}
    assert response.status_code == 201
    mock_add.assert_called_with("test.com")


@pytest.mark.asyncio
async def test_add_scrapable_domain_as_user():
    app.dependency_overrides[get_current_user] = lambda: {"uid": "user-uid"}

    with patch("backend.app.main.firestore_repo.get_user") as mock_db_user:
        mock_db_user.return_value = {"role": "user"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/scrapable-domains", json={"domain": "test.com"}
            )

    app.dependency_overrides = {}
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_trigger_scrape():
    app.dependency_overrides[get_current_user] = lambda: {"uid": "admin-uid"}

    with patch("backend.app.main.firestore_repo.get_user") as mock_db_user:
        mock_db_user.return_value = {"role": "admin"}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("/api/scrape")

    app.dependency_overrides = {}
    assert response.status_code == 202
