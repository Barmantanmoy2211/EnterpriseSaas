from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    name: str
    resource_type: str = "equipment"
    description: str = ""
    capacity: float = 1
    capacity_unit: str = "hours"
    status: str = "available"
    org_node_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResourceUpdate(BaseModel):
    name: str | None = None
    resource_type: str | None = None
    description: str | None = None
    capacity: float | None = None
    capacity_unit: str | None = None
    status: str | None = None
    org_node_id: str | None = None
    metadata: dict[str, Any] | None = None


class ResourceResponse(BaseModel):
    id: str
    name: str
    resource_type: str
    description: str
    capacity: float
    capacity_unit: str
    status: str
    org_node_id: str | None
    metadata: dict[str, Any]


class AllocationCreate(BaseModel):
    resource_id: str
    project_id: str | None = None
    allocated_units: float
    start_date: date
    end_date: date
    notes: str = ""


class AllocationResponse(BaseModel):
    id: str
    resource_id: str
    project_id: str | None
    allocated_units: float
    start_date: date
    end_date: date
    notes: str
    allocated_by: str
