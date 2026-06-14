from typing import Any

from pydantic import BaseModel, Field


class InventoryItemCreate(BaseModel):
    sku: str
    name: str
    description: str = ""
    quantity: float = 0
    unit: str = "ea"
    warehouse_location: str = ""
    reorder_level: float = 0
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: float | None = None
    unit: str | None = None
    warehouse_location: str | None = None
    reorder_level: float | None = None
    status: str | None = None
    metadata: dict[str, Any] | None = None


class InventoryItemResponse(BaseModel):
    id: str
    sku: str
    name: str
    description: str
    quantity: float
    unit: str
    warehouse_location: str
    reorder_level: float
    status: str
    metadata: dict[str, Any]


class InventoryMovementCreate(BaseModel):
    item_id: str
    movement_type: str
    quantity: float
    reference: str = ""
    notes: str = ""


class InventoryMovementResponse(BaseModel):
    id: str
    item_id: str
    movement_type: str
    quantity: float
    reference: str
    notes: str
    performed_by: str
