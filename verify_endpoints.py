from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

# Add backend to sys.path
sys.path.append(os.getcwd())

# Mock firebase stuff before importing main
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.auth"] = MagicMock()
sys.modules["firebase_admin.storage"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()

# Mock the FirestoreRepo
from backend.app.firestore_repo import FirestoreRepo
FirestoreRepo.get_user = MagicMock(return_value={"uid": "test_admin", "role": "admin", "email": "admin@example.com"})
FirestoreRepo.get_job_titles = MagicMock(return_value=[{"id": "1", "title": "Software Engineer"}])
FirestoreRepo.get_scrape_history = MagicMock(return_value=[])
FirestoreRepo.get_users = MagicMock(return_value=[])

# Mock dependencies
from backend.app.security import get_current_user
from backend.app.main import app

# Override the dependency
def mock_get_current_user():
    return {"uid": "test_admin", "email": "admin@example.com", "role": "admin"}

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_endpoints():
    print("Testing /api/admin/job-titles/...")
    response = client.get("/api/admin/job-titles/")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200

    print("Testing /api/scrape-history/...")
    response = client.get("/api/scrape-history/")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200

    print("Testing /api/users/...")
    response = client.get("/api/users/")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200

if __name__ == "__main__":
    try:
        test_endpoints()
        print("All endpoints reachable!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
