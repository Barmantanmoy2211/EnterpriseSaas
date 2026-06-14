from typing import Any

from beanie import PydanticObjectId
from pydantic import EmailStr, Field

from app.shared.base_model import TenantDocument


class JobPosting(TenantDocument):
    title: str
    description: str = ""
    org_node_id: PydanticObjectId | None = None
    status: str = "open"
    requirements: list[str] = Field(default_factory=list)
    location: str = ""
    employment_type: str = "full_time"

    class Settings:
        name = "job_postings"
        indexes = [[("tenant_id", 1), ("status", 1)]]


class Candidate(TenantDocument):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = ""
    resume_url: str | None = None
    source: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "candidates"
        indexes = [[("tenant_id", 1), ("email", 1)]]


class JobApplication(TenantDocument):
    job_id: PydanticObjectId
    candidate_id: PydanticObjectId
    status: str = "applied"
    notes: str = ""
    stage_history: list[dict[str, Any]] = Field(default_factory=list)

    class Settings:
        name = "job_applications"
        indexes = [
            [("tenant_id", 1), ("job_id", 1)],
            [("tenant_id", 1), ("candidate_id", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]
