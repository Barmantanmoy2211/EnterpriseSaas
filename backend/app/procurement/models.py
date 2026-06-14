from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.shared.base_model import TenantDocument


class PurchaseOrderLine(BaseModel):
    sku: str = ""
    description: str = ""
    quantity: float = 1
    unit_price: float = 0


class Supplier(TenantDocument):
    name: str
    code: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "suppliers"
        indexes = [[("tenant_id", 1), ("code", 1)]]


class PurchaseOrder(TenantDocument):
    po_number: str
    supplier_id: PydanticObjectId
    status: str = "draft"
    lines: list[PurchaseOrderLine] = Field(default_factory=list)
    total_amount: float = 0
    currency: str = "USD"
    requested_by: PydanticObjectId
    expected_delivery: date | None = None
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "purchase_orders"
        indexes = [
            [("tenant_id", 1), ("po_number", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]
