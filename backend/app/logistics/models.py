from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.shared.base_model import TenantDocument


class ShipmentItem(BaseModel):
    sku: str = ""
    description: str = ""
    quantity: float = 1


class Shipment(TenantDocument):
    shipment_number: str
    origin: str = ""
    destination: str = ""
    carrier: str = ""
    tracking_number: str = ""
    status: str = "pending"
    items: list[ShipmentItem] = Field(default_factory=list)
    scheduled_date: date | None = None
    delivered_date: date | None = None
    created_by: PydanticObjectId
    purchase_order_id: PydanticObjectId | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "shipments"
        indexes = [
            [("tenant_id", 1), ("shipment_number", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]
