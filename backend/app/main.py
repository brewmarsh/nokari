@app.post("/api/jobs/{job_id}/find-similar", status_code=status.HTTP_202_ACCEPTED)
def find_similar_jobs(job_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")  # Use 'uid' from Firebase decoded token
    task_id = str(uuid.uuid4())

    message = {"job_id": job_id, "user_id": user_id, "task_id": task_id}

    try:
        sqs_client.send_message(
            QueueUrl=SIMILARITY_QUEUE_URL, MessageBody=json.dumps(message)
        )
        return {"message": "Similarity search initiated.", "task_id": task_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate similarity search: {e}",
        )


@app.post("/api/jobs/{job_id}/hide", status_code=status.HTTP_200_OK)
def hide_job(job_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token: no uid")

    firestore_repo.update_user_job_interaction(user_id, job_id, {"hidden": True})
    return {"message": "Job hidden"}


@app.post("/api/jobs/{job_id}/pin", status_code=status.HTTP_200_OK)
def pin_job(job_id: str, is_pinned: bool, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token: no uid")

    firestore_repo.update_user_job_interaction(user_id, job_id, {"pinned": is_pinned})
    return {"message": "Job pinned status updated"}


@app.post("/api/companies/{company_name}/hide", status_code=status.HTTP_200_OK)
def hide_company(company_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token: no uid")

    firestore_repo.hide_company_for_user(user_id, company_name)
    return {"message": "Company hidden"}


@app.post("/api/resumes/upload")
