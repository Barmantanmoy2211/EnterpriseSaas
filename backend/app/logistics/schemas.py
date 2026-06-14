from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.logistics.models import ShipmentItem


class ShipmentCreate(BaseModel):
    shipment_number: str
    origin: str = ""
    destination: str = ""
    carrier: str = ""
    tracking_number: str = ""
    status: str = "pending"
    items: list[ShipmentItem] = Field(default_factory=list)
    scheduled_date: date | None = None
    purchase_order_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ShipmentUpdate(BaseModel):
    origin: str | None = None
    destination: str | None = None
    carrier: str | None = None
    tracking_number: str | None = None
    status: str | None = None
    items: list[ShipmentItem] | None = None
    scheduled_date: date | None = None
    delivered_date: date | None = None
    metadata: dict[str, Any] | None = None


class ShipmentResponse(BaseModel):
    id: str
    shipment_number: str
    origin: str
    destination: str
    carrier: str
    tracking_number: str
    status: str
    items: list[ShipmentItem]
    scheduled_date: date | None
    delivered_date: date | None
    created_by: str
    purchase_order_id: str | None
    metadata: dict[str, Any]
