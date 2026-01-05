from typing import Any, Dict, List, Optional
from firebase_admin import firestore
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
            self.db.collection("users").document(user_id).set(user_data, merge=True)
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

    def get_users(self) -> List[Dict[str, Any]]:
        try:
            docs = self.db.collection("users").stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get users: {e}",
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
        self,
        locations: Optional[List[str]] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 20,
        last_doc_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            query = self.db.collection("job_postings")

            if locations and len(locations) > 0:
                query = query.where(
                    "searchable_locations", "array_contains_any", locations
                )

            if title:
                query = query.where("title", "==", title)

            if company:
                query = query.where("company", "==", company)

            # Order by posting_date desc
            query = query.order_by("posting_date", direction=firestore.Query.DESCENDING)

            if last_doc_id:
                last_doc = (
                    self.db.collection("job_postings").document(last_doc_id).get()
                )
                if last_doc.exists:
                    query = query.start_after(last_doc)

            query = query.limit(limit)

            docs = query.stream()
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

    def update_user_job_interaction(
        self, user_id: str, job_id: str, interaction_data: Dict[str, Any]
    ):
        try:
            self.db.collection("users").document(user_id).collection(
                "job_interactions"
            ).document(job_id).set(interaction_data, merge=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user job interaction: {e}",
            )

    def hide_company_for_user(self, user_id: str, company_name: str):
        try:
            self.db.collection("users").document(user_id).collection(
                "hidden_companies"
            ).document(company_name).set({"name": company_name})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to hide company for user: {e}",
            )

    def add_scrapable_domain(self, domain: str):
        try:
            # Check for duplicates
            docs = (
                self.db.collection("scrapable_domains")
                .where("domain", "==", domain)
                .limit(1)
                .get()
            )
            for _ in docs:
                # Domain already exists
                return

            self.db.collection("scrapable_domains").add({"domain": domain})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add scrapable domain: {e}",
            )

    def get_scrapable_domains(self) -> List[Dict[str, Any]]:
        try:
            docs = self.db.collection("scrapable_domains").stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get scrapable domains: {e}",
            )

    def get_scrape_schedule(self) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.collection("settings").document("scrape_schedule").get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get scrape schedule: {e}",
            )

    def put_scrape_schedule(self, schedule_data: Dict[str, Any]):
        try:
            self.db.collection("settings").document("scrape_schedule").set(
                schedule_data, merge=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to put scrape schedule: {e}",
            )

    def add_job_title(self, title: str):
        try:
            # Check for duplicates
            docs = (
                self.db.collection("job_titles")
                .where("title", "==", title)
                .limit(1)
                .get()
            )
            for _ in docs:
                # Job title already exists
                return

            self.db.collection("job_titles").add({"title": title})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add job title: {e}",
            )

    def get_job_titles(self) -> List[Dict[str, Any]]:
        try:
            docs = self.db.collection("job_titles").stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get job titles: {e}",
            )

    def delete_job_title(self, job_title_id: str):
        try:
            self.db.collection("job_titles").document(job_title_id).delete()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete job title: {e}",
            )

    def add_scrape_history_entry(self, entry: Dict[str, Any]):
        try:
            self.db.collection("scrape_history").add(entry)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add scrape history entry: {e}",
            )

    def get_scrape_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            docs = (
                self.db.collection("scrape_history")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get scrape history: {e}",
            )
