from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Task(TenantDocument):
    title: str
    description: str = ""
    project_id: PydanticObjectId | None = None
    assignee_id: PydanticObjectId | None = None
    created_by: PydanticObjectId
    status: str = "todo"
    priority: str = "medium"
    due_date: date | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "tasks"
        indexes = [
            [("tenant_id", 1), ("project_id", 1)],
            [("tenant_id", 1), ("assignee_id", 1), ("status", 1)],
        ]
