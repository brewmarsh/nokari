from typing import Any, Dict, List, Optional

from firebase_admin.firestore import Client
from fastapi import HTTPException, status



class FirestoreRepo:
    """
    A repository for interacting with the Firestore database.
    This class abstracts the Firestore calls and provides a clean interface for the application logic.
    """

    def __init__(self, db_client: Client):
        self.db = db_client

    def put_user(self, user_id: str, user_data: Dict[str, Any]):
        try:
            self.db.collection("users").document(user_id).set(user_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to put user: {e}",
            )

    def get_user(self, user_id: str):
        try:
            doc = self.db.collection("users").document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
                user_data["id"] = doc.id  # Add document ID
                return user_data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user: {e}",
            )

    def get_user_by_email(self, email: str):
        try:
            docs = (
                self.db.collection("users").where("email", "==", email).limit(1).get()
            )
            for doc in docs:
                user_data = doc.to_dict()
                user_data["id"] = doc.id  # Add document ID
                return user_data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user by email: {e}",
            )

    def update_user_resume(self, user_id: str, s3_link: str):
        try:
            self.db.collection("users").document(user_id).update(
                {"resume_s3_link": s3_link}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user resume: {e}",
            )

    def put_job_posting(self, job_id: str, job_data: Dict[str, Any]):
        try:
            self.db.collection("job_postings").document(job_id).set(job_data)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to put job posting: {e}",
            )

    def get_job_posting(self, job_id: str):
        try:
            doc = self.db.collection("job_postings").document(job_id).get()
            if doc.exists:
                job_data = doc.to_dict()
                job_data["id"] = doc.id  # Add document ID
                return job_data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job posting: {e}",
            )

    def search_jobs(
        self, location: Optional[str] = None, title: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            query = self.db.collection("job_postings")
            if location:
                query = query.where("locations", "array_contains", location)
            if title:
                query = query.where("title", "==", title)

            docs = query.get()
            return [{**doc.to_dict(), "id": doc.id} for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search jobs: {e}",
            )

    def put_similarity_result(self, task_id: str, similar_job_ids: List[str]):
        try:
            self.db.collection("similarity_results").document(task_id).set(
                {"similar_job_ids": similar_job_ids}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to put similarity result: {e}",
            )
