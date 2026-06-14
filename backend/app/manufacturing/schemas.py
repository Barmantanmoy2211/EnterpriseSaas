from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.manufacturing.models import BomComponent


class BomCreate(BaseModel):
    product_sku: str
    name: str
    description: str = ""
    components: list[BomComponent] = Field(default_factory=list)
    version: int = 1
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class BomUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    components: list[BomComponent] | None = None
    version: int | None = None
    is_active: bool | None = None
    metadata: dict[str, Any] | None = None


class BomResponse(BaseModel):
    id: str
    product_sku: str
    name: str
    description: str
    components: list[BomComponent]
    version: int
    is_active: bool
    metadata: dict[str, Any]


class ProductionOrderCreate(BaseModel):
    order_number: str
    bom_id: str
    quantity: float
    status: str = "planned"
    scheduled_start: date | None = None
    scheduled_end: date | None = None
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductionOrderUpdate(BaseModel):
    quantity: float | None = None
    status: str | None = None
    scheduled_start: date | None = None
    scheduled_end: date | None = None
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class ProductionOrderResponse(BaseModel):
    id: str
    order_number: str
    bom_id: str
    quantity: float
    status: str
    scheduled_start: date | None
    scheduled_end: date | None
    created_by: str
    notes: str
    metadata: dict[str, Any]
