from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.procurement.models import PurchaseOrderLine


class SupplierCreate(BaseModel):
    name: str
    code: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)


class SupplierUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str | None = None
    metadata: dict[str, Any] | None = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    code: str
    contact_name: str
    contact_email: str
    contact_phone: str
    status: str
    metadata: dict[str, Any]


class PurchaseOrderCreate(BaseModel):
    po_number: str
    supplier_id: str
    status: str = "draft"
    lines: list[PurchaseOrderLine] = Field(default_factory=list)
    currency: str = "USD"
    expected_delivery: date | None = None
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class PurchaseOrderUpdate(BaseModel):
    status: str | None = None
    lines: list[PurchaseOrderLine] | None = None
    expected_delivery: date | None = None
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class PurchaseOrderResponse(BaseModel):
    id: str
    po_number: str
    supplier_id: str
    status: str
    lines: list[PurchaseOrderLine]
    total_amount: float
    currency: str
    requested_by: str
    expected_delivery: date | None
    notes: str
    metadata: dict[str, Any]
