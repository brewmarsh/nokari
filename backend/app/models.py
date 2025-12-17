from datetime import datetime
from typing import Optional, List

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
    link: Optional[str] = None
    locations: Optional[List[str]] = None
    is_pinned: Optional[bool] = False


class ScrapableDomain(BaseModel):
    id: str
    domain: str


class CreateDomainRequest(BaseModel):
    domain: str


class JobTitle(BaseModel):
    id: str
    title: str


class CreateJobTitleRequest(BaseModel):
    title: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    preferred_work_arrangement: List[str] = []
    created_at: Optional[str] = None
