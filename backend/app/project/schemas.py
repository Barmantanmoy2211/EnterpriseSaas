from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    code: str = ""
    status: str = "active"
    priority: str = "medium"
    owner_id: str | None = None
    org_node_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    code: str | None = None
    status: str | None = None
    priority: str | None = None
    owner_id: str | None = None
    org_node_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    code: str
    status: str
    priority: str
    owner_id: str | None
    org_node_id: str | None
    start_date: date | None
    end_date: date | None
    metadata: dict[str, Any]
