from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    project_id: str | None = None
    assignee_id: str | None = None
    status: str = "todo"
    priority: str = "medium"
    due_date: date | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    project_id: str | None = None
    assignee_id: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: date | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    project_id: str | None
    assignee_id: str | None
    created_by: str
    status: str
    priority: str
    due_date: date | None
    tags: list[str]
    metadata: dict[str, Any]
