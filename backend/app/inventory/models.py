from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class InventoryItem(TenantDocument):
    sku: str
    name: str
    description: str = ""
    quantity: float = 0
    unit: str = "ea"
    warehouse_location: str = ""
    reorder_level: float = 0
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "inventory_items"
        indexes = [
            [("tenant_id", 1), ("sku", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]


class InventoryMovement(TenantDocument):
    item_id: PydanticObjectId
    movement_type: str
    quantity: float
    reference: str = ""
    notes: str = ""
    performed_by: PydanticObjectId

    class Settings:
        name = "inventory_movements"
        indexes = [[("tenant_id", 1), ("item_id", 1)]]
