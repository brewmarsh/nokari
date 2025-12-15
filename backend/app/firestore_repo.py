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

    def update_user_job_interaction(self, user_id: str, job_id: str, interaction_data: Dict[str, Any]):
        try:
            self.db.collection("users").document(user_id).collection("job_interactions").document(job_id).set(
                interaction_data, merge=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user job interaction: {e}",
            )

    def hide_company_for_user(self, user_id: str, company_name: str):
        try:
            self.db.collection("users").document(user_id).collection("hidden_companies").document(company_name).set(
                {"name": company_name}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to hide company for user: {e}",
            )

    def add_scrapable_domain(self, domain: str):
