import os
import json
import sys
import pytest
from unittest.mock import MagicMock, patch

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

# Mock the entire firebase_admin module to prevent it from trying to initialize.
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.storage"] = MagicMock()
sys.modules["firebase_admin.auth"] = MagicMock()

# Now it's safe to import the app
from backend.app.main import app  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


@pytest.fixture
def mock_auth_repo():
    with patch("backend.app.main.firebase_auth_repo", autospec=True) as mock_repo:
        yield mock_repo


@pytest.fixture
def mock_firestore_repo():
    with patch("backend.app.main.firestore_repo", autospec=True) as mock_repo:
        yield mock_repo


@pytest.mark.asyncio
async def test_register_user_success(
    mock_auth_repo: MagicMock, mock_firestore_repo: MagicMock
):
    mock_auth_repo.create_user.return_value = "some_uid"
    mock_firestore_repo.put_user.return_value = None

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/register/",
            json={"email": "test@example.com", "password": "password123"},
        )

    assert response.status_code == 201
    assert "User registered successfully" in response.json()["message"]
    mock_auth_repo.create_user.assert_called_once_with(
        "test@example.com", "password123"
    )
    mock_firestore_repo.put_user.assert_called_once_with(
        "some_uid", {"email": "test@example.com", "role": "user"}
    )


@pytest.mark.asyncio
async def test_register_user_failure(
    mock_auth_repo: MagicMock, mock_firestore_repo: MagicMock
):
    mock_auth_repo.create_user.side_effect = Exception("User already exists")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/register/",
            json={"email": "test@example.com", "password": "password123"},
        )

    assert response.status_code == 400
    assert "User already exists" in response.json()["detail"]
    mock_firestore_repo.put_user.assert_not_called()


@pytest.mark.asyncio
async def test_login_user_success(mock_auth_repo: MagicMock):
    mock_auth_repo.verify_id_token.return_value = {"uid": "some_uid"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/login/", json={"id_token": "some_id_token"})

    assert response.status_code == 200
    assert response.json() == {"message": "Authentication successful"}
    mock_auth_repo.verify_id_token.assert_called_once_with("some_id_token")


@pytest.mark.asyncio
async def test_login_user_failure(mock_auth_repo: MagicMock):
    mock_auth_repo.verify_id_token.side_effect = Exception("Invalid ID token")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/login/", json={"id_token": "invalid_id_token"})

    assert response.status_code == 401
    assert "Invalid ID token" in response.json()["detail"]
