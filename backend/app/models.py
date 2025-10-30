from datetime import datetime

from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    description: str
    work_arrangement: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateJobRequest(BaseModel):
    title: str
    company: str
    location: str
    description: str
    work_arrangement: str


class JobPostResponse(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    work_arrangement: str


class CreateDomainRequest(BaseModel):
    domain_name: str
