from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    description: str
    work_arrangement: str
    posting_date: Optional[datetime] = None
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
    posting_date: Optional[datetime] = None


class ScrapableDomain(BaseModel):
    id: str
    domain: str


class CreateDomainRequest(BaseModel):
    domain: str
