from typing import Any

from pydantic import BaseModel, EmailStr, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    org_node_id: str | None = None
    requirements: list[str] = Field(default_factory=list)
    location: str = ""
    employment_type: str = "full_time"


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    requirements: list[str] | None = None
    location: str | None = None


class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    org_node_id: str | None
    status: str
    requirements: list[str]
    location: str
    employment_type: str


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = ""
    resume_url: str | None = None
    source: str = ""


class CandidateResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    resume_url: str | None
    source: str


class ApplicationCreate(BaseModel):
    job_id: str
    candidate_id: str
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    status: str
    notes: str
    stage_history: list[dict[str, Any]]
