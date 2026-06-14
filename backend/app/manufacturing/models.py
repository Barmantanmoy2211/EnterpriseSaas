from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.shared.base_model import TenantDocument


class BomComponent(BaseModel):
    sku: str
    name: str = ""
    quantity: float = 1
    unit: str = "ea"


class BillOfMaterials(TenantDocument):
    product_sku: str
    name: str
    description: str = ""
    components: list[BomComponent] = Field(default_factory=list)
    version: int = 1
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "bills_of_materials"
        indexes = [[("tenant_id", 1), ("product_sku", 1)]]


class ProductionOrder(TenantDocument):
    order_number: str
    bom_id: PydanticObjectId
    quantity: float
    status: str = "planned"
    scheduled_start: date | None = None
    scheduled_end: date | None = None
    created_by: PydanticObjectId
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "production_orders"
        indexes = [
            [("tenant_id", 1), ("order_number", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]
