import json
import os
import uuid
from typing import List, Optional

import boto3
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel

from backend.app import models
from backend.app.cognito_repo import CognitoRepo
from backend.app.dynamo_repo import DynamoRepo
from backend.app.security import get_current_user

app = FastAPI()
dynamo_repo = DynamoRepo(table_name="NokariData")
cognito_repo = CognitoRepo()
s3_client = boto3.client("s3")
# Explicitly set region
sqs_client = boto3.client("sqs", region_name="us-east-1")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "nokari-resumes")
SIMILARITY_QUEUE_URL = os.environ.get(
    "SIMILARITY_QUEUE_URL",
    "https://sqs.us-east-1.amazonaws.com/123456789012/nokari-similarity-queue",
)


class AuthRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access: str
    refresh: str


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register(register_request: AuthRequest):
    try:
        cognito_repo.sign_up(register_request.email, register_request.password)
        return {"message": "User registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/login/", response_model=TokenResponse)
def login(login_request: AuthRequest):
    try:
        auth_result = cognito_repo.sign_in(login_request.email, login_request.password)
        return TokenResponse(
            access=auth_result["AccessToken"], refresh=auth_result["RefreshToken"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post("/jobs", response_model=models.JobPostResponse)
def create_job(
    job_request: models.CreateJobRequest, current_user: dict = Depends(get_current_user)
):
    if (
        "cognito:groups" not in current_user
        or "Admin" not in current_user["cognito:groups"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    job_id = str(uuid.uuid4())
    job_data = job_request.model_dump()
    dynamo_repo.put_job_posting(job_id, job_data)
    return models.JobPostResponse(job_id=job_id, **job_data)


@app.get("/jobs/{job_id}", response_model=models.JobPostResponse)
def get_job(job_id: str):
    job_data = dynamo_repo.get_job_posting(job_id)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return models.JobPostResponse(job_id=job_id, **job_data)


@app.get("/jobs", response_model=List[models.JobPostResponse])
def search_jobs(
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    work_arrangement: Optional[str] = None,
):
    jobs = dynamo_repo.search_jobs(location=location, title=title)
    return [
        models.JobPostResponse(job_id=job["PK"].split("#")[1], **job) for job in jobs
    ]


@app.post("/jobs/{job_id}/find-similar", status_code=status.HTTP_202_ACCEPTED)
def find_similar_jobs(job_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("sub")
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


@app.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")  # 'sub' is the user ID from Cognito JWT
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found in token"
        )

    file_key = f"resumes/{user_id}/{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, file_key)
        s3_link = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_key}"

        dynamo_repo.update_user_resume(user_id, s3_link)

        return {"message": "Resume uploaded successfully", "s3_link": s3_link}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {e}",
        )


handler = Mangum(app)
