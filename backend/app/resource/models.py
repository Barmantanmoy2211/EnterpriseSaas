from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Resource(TenantDocument):
    name: str
    resource_type: str = "equipment"
    description: str = ""
    capacity: float = 1
    capacity_unit: str = "hours"
    status: str = "available"
    org_node_id: PydanticObjectId | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "resources"
        indexes = [
            [("tenant_id", 1), ("resource_type", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]


class ResourceAllocation(TenantDocument):
    resource_id: PydanticObjectId
    project_id: PydanticObjectId | None = None
    allocated_units: float
    start_date: date
    end_date: date
    notes: str = ""
    allocated_by: PydanticObjectId

    class Settings:
        name = "resource_allocations"
        indexes = [[("tenant_id", 1), ("resource_id", 1)]]
