import json
import os
import uuid
from typing import List, Optional

import boto3
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel

from backend.app import models
from backend.app.firestore_repo import FirestoreRepo
from backend.app.scraper import run_scraper
from backend.app.firebase_auth_repo import FirebaseAuthRepo
from backend.app.firebase_config import db, firebase_storage
from backend.app.security import get_current_user

app = FastAPI()
firestore_repo = FirestoreRepo(db_client=db)
firebase_auth_repo = FirebaseAuthRepo()


def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid token: no uid")

    user_data = firestore_repo.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=403, detail="User not found")

    if user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user_data


# Explicitly set region
sqs_client = boto3.client("sqs", region_name="us-east-1")
SIMILARITY_QUEUE_URL = os.environ.get(
    "SIMILARITY_QUEUE_URL",
    "https://sqs.us-east-1.amazonaws.com/123456789012/nokari-similarity-queue",
)


class AuthRequest(BaseModel):
    email: str
    password: str


class FirebaseLoginRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    message: str = "Authentication successful"


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )


@app.get("/api/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/register/", status_code=status.HTTP_201_CREATED)
def register(register_request: AuthRequest):
    try:
        user_uid = firebase_auth_repo.create_user(
            register_request.email, register_request.password
        )
        # Optionally, create a user document in Firestore with additional data
        firestore_repo.put_user(
            user_uid, {"email": register_request.email, "role": "user"}
        )
        return {"message": f"User registered successfully with UID: {user_uid}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/login/", response_model=TokenResponse)
def login(login_request: FirebaseLoginRequest):
    try:
        firebase_auth_repo.verify_id_token(login_request.id_token)
        # Optionally, you can perform additional checks here, e.g., if the user exists in your Firestore
        return TokenResponse(message="Authentication successful")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post("/api/jobs", response_model=models.JobPostResponse)
def create_job(
    job_request: models.CreateJobRequest, current_user: dict = Depends(get_current_user)
):
    # Admin check will be implemented using Firebase Custom Claims or Firestore user roles later
    # For now, assuming authenticated user can create jobs
    # if (
    #     "cognito:groups" not in current_user
    #     or "Admin" not in current_user["cognito:groups"]
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
    # )

    job_id = str(uuid.uuid4())
    job_data = job_request.model_dump()
    firestore_repo.put_job_posting(job_id, job_data)
    return models.JobPostResponse(job_id=job_id, **job_data)


@app.get("/api/jobs/{job_id}", response_model=models.JobPostResponse)
def get_job(job_id: str):
    job_data = firestore_repo.get_job_posting(job_id)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return models.JobPostResponse(job_id=job_id, **job_data)


@app.get("/api/jobs", response_model=List[models.JobPostResponse])
def search_jobs(
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    work_arrangement: Optional[str] = None,
    limit: int = 20,
    last_doc_id: Optional[str] = None,
):
    jobs = firestore_repo.search_jobs(
        location=location, title=title, limit=limit, last_doc_id=last_doc_id
    )
    # Firestore does not automatically include the document ID in the data.
    # We need to add it manually if it's part of the response model.
    # Assuming job_id is the document ID.
    return [models.JobPostResponse(job_id=job.get("id", ""), **job) for job in jobs]


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


@app.post("/api/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get(
        "uid"
    )  # 'uid' is the user ID from Firebase decoded token
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found in token"
        )

    try:
        bucket = firebase_storage.bucket()
        file_path = f"resumes/{user_id}/{file.filename}"
        blob = bucket.blob(file_path)

        # Upload the file
        blob.upload_from_file(file.file, content_type=file.content_type)

        # Make the blob publicly accessible (optional, depending on your security needs)
        # Or generate a signed URL for temporary access
        blob.make_public()
        firebase_url = blob.public_url

        firestore_repo.update_user_resume(user_id, firebase_url)

        return {"message": "Resume uploaded successfully", "firebase_url": firebase_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {e}",
        )


@app.get("/api/scrapable-domains", response_model=List[models.ScrapableDomain])
def get_scrapable_domains(current_user: dict = Depends(get_current_admin_user)):
    return firestore_repo.get_scrapable_domains()


@app.post("/api/scrapable-domains", status_code=status.HTTP_201_CREATED)
def add_scrapable_domain(
    domain_request: models.CreateDomainRequest,
    current_user: dict = Depends(get_current_admin_user),
):
    firestore_repo.add_scrapable_domain(domain_request.domain)
    return {"message": f"Domain {domain_request.domain} added."}


@app.post("/api/scrape", status_code=status.HTTP_202_ACCEPTED)
def trigger_scrape(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_admin_user),
):
    background_tasks.add_task(run_scraper)
    return {"message": "Scraping started in background."}


handler = Mangum(app)
