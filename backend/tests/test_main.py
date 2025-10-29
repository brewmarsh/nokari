import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from backend.app.main import app, get_current_user


# Mock users for dependency injection
def mock_admin_user():
    return {"sub": "test-admin-123", "cognito:groups": ["Admin"]}


def mock_regular_user():
    return {"sub": "test-user-456", "cognito:groups": ["User"]}


@pytest.fixture
def mock_dynamo_repo():
    with patch("backend.app.main.dynamo_repo", autospec=True) as mock_repo:
        yield mock_repo


@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio
async def test_create_job_as_admin(mock_dynamo_repo: MagicMock):
    app.dependency_overrides[get_current_user] = mock_admin_user
    job_data = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "description": "A job opening.",
        "work_arrangement": "Remote",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/jobs", json=job_data)

    assert response.status_code == 200
    app.dependency_overrides = {}  # Reset overrides


@pytest.mark.asyncio
async def test_create_job_as_non_admin(mock_dynamo_repo: MagicMock):
    app.dependency_overrides[get_current_user] = mock_regular_user
    job_data = {
        "title": "Test",
        "company": "Test",
        "location": "Test",
        "description": "Test",
        "work_arrangement": "Remote",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/jobs", json=job_data)

    assert response.status_code == 403
    app.dependency_overrides = {}  # Reset overrides


@pytest.mark.asyncio
async def test_get_job(mock_dynamo_repo: MagicMock):
    job_id = "test-job-id"
    mock_job_data = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "description": "A job opening.",
        "work_arrangement": "Remote",
    }
    mock_dynamo_repo.get_job_posting.return_value = mock_job_data

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["title"] == mock_job_data["title"]


@pytest.mark.asyncio
async def test_search_jobs(mock_dynamo_repo: MagicMock):
    mock_job_data = [
        {
            "PK": "JOB#123",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "work_arrangement": "Remote",
        }
    ]
    mock_dynamo_repo.search_jobs.return_value = mock_job_data

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/jobs?location=Remote")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
@patch("backend.app.main.s3_client")
async def test_upload_resume(mock_s3_client: MagicMock, mock_dynamo_repo: MagicMock):
    app.dependency_overrides[get_current_user] = mock_regular_user
    file_content = b"This is a test resume."

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/resumes/upload",
            files={"file": ("resume.txt", file_content, "text/plain")},
        )

    assert response.status_code == 200
    assert "s3_link" in response.json()
    mock_s3_client.upload_fileobj.assert_called_once()
    mock_dynamo_repo.update_user_resume.assert_called_once()
    app.dependency_overrides = {}  # Reset overrides


@pytest.mark.asyncio
@patch("backend.app.main.sqs_client")
async def test_find_similar_jobs(
    mock_sqs_client: MagicMock, mock_dynamo_repo: MagicMock
):
    app.dependency_overrides[get_current_user] = mock_regular_user
    job_id = "test-job-id"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(f"/jobs/{job_id}/find-similar")

    assert response.status_code == 202
    assert "task_id" in response.json()
    mock_sqs_client.send_message.assert_called_once()
    app.dependency_overrides = {}  # Reset overrides
