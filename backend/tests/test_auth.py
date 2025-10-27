import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from backend.app.main import app

@pytest.fixture
def mock_cognito_repo():
    with patch('backend.app.main.cognito_repo', autospec=True) as mock_repo:
        yield mock_repo

@pytest.mark.asyncio
async def test_register_user_success(mock_cognito_repo: MagicMock):
    mock_cognito_repo.sign_up.return_value = True

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/register/", json={"email": "test@example.com", "password": "password123"})

    assert response.status_code == 201
    assert response.json() == {"message": "User registered successfully."}
    mock_cognito_repo.sign_up.assert_called_once_with("test@example.com", "password123")

@pytest.mark.asyncio
async def test_register_user_failure(mock_cognito_repo: MagicMock):
    mock_cognito_repo.sign_up.side_effect = Exception("User already exists")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/register/", json={"email": "test@example.com", "password": "password123"})

    assert response.status_code == 400
    assert "User already exists" in response.json()["detail"]
