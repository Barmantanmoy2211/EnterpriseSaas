from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Project(TenantDocument):
    name: str
    description: str = ""
    code: str = ""
    status: str = "active"
    priority: str = "medium"
    owner_id: PydanticObjectId | None = None
    org_node_id: PydanticObjectId | None = None
    start_date: date | None = None
    end_date: date | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "projects"
        indexes = [
            [("tenant_id", 1), ("status", 1)],
            [("tenant_id", 1), ("code", 1)],
        ]
