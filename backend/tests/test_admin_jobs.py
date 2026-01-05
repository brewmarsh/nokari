
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

# Mock Firebase Auth
@pytest.fixture
def mock_firebase_auth(mocker):
    mock_verify = mocker.patch("backend.app.firebase_auth_repo.FirebaseAuthRepo.verify_id_token")
    mock_verify.return_value = {"uid": "test_admin_uid", "email": "admin@example.com"}
    return mock_verify

# Mock Firestore
@pytest.fixture
def mock_firestore(mocker):
    mock_repo = mocker.patch("backend.app.main.firestore_repo")

    # Mock admin user check
    mock_repo.get_user.return_value = {"role": "admin", "uid": "test_admin_uid"}

    return mock_repo

@pytest.fixture
def mock_scraping_logic(mocker):
    return mocker.patch("backend.app.main.scraping_logic")


@pytest.mark.asyncio
async def test_get_admin_jobs(mock_firebase_auth, mock_firestore):
    mock_firestore.search_jobs.return_value = [
        {
            "id": "job1",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "work_arrangement": "Remote",
            "link": "http://example.com/job1"
        }
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # We need to bypass the actual authentication middleware or mock it effectively.
        # Since 'get_current_user' depends on 'verify_id_token', mocking 'verify_id_token' isn't enough
        # because the dependency override isn't set up here.
        # However, we can override the dependency.

        from backend.app.security import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"uid": "test_admin_uid", "email": "admin@example.com"}

        response = await ac.get("/api/admin/jobs/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["job_id"] == "job1"

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_delete_admin_job(mock_firebase_auth, mock_firestore):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        from backend.app.security import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"uid": "test_admin_uid", "email": "admin@example.com"}

        response = await ac.delete("/api/admin/jobs/job1/")

    assert response.status_code == 200
    mock_firestore.delete_job_posting.assert_called_with("job1")
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_rescrape_admin_job(mock_firebase_auth, mock_firestore, mock_scraping_logic):
    mock_firestore.get_job_posting.return_value = {"link": "http://example.com/job1", "title": "Old Title"}
    mock_scraping_logic.scrape_job_details.return_value = {"title": "New Title", "description": "New Desc"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        from backend.app.security import get_current_user
        app.dependency_overrides[get_current_user] = lambda: {"uid": "test_admin_uid", "email": "admin@example.com"}

        response = await ac.post("/api/admin/jobs/job1/rescrape/")

    assert response.status_code == 200
    mock_scraping_logic.scrape_job_details.assert_called_with("http://example.com/job1")
    # Verify update called
    args, _ = mock_firestore.put_job_posting.call_args
    assert args[0] == "job1"
    assert args[1]["title"] == "New Title"

    app.dependency_overrides = {}
