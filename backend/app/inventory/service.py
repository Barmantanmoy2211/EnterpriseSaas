from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.inventory.models import InventoryItem
from app.inventory.repository import InventoryRepository
from app.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryMovementCreate,
    InventoryMovementResponse,
)
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError, ValidationError


class InventoryService:
    @staticmethod
    def _item_response(item: InventoryItem) -> InventoryItemResponse:
        return InventoryItemResponse(
            id=str(item.id),
            sku=item.sku,
            name=item.name,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            warehouse_location=item.warehouse_location,
            reorder_level=item.reorder_level,
            status=item.status,
            metadata=item.metadata,
        )

    @staticmethod
    async def _index(item: InventoryItem) -> None:
        await SearchRepository.upsert(
            str(item.tenant_id),
            "inventory_item",
            str(item.id),
            item.name,
            item.description,
            [item.sku, item.warehouse_location],
            {"status": item.status, "quantity": item.quantity},
        )

    @staticmethod
    async def list_items(tenant_id: str, status: str | None = None) -> list[InventoryItemResponse]:
        items = await InventoryRepository.list_items(tenant_id, status)
        return [InventoryService._item_response(i) for i in items]

    @staticmethod
    async def get_item(tenant_id: str, item_id: str) -> InventoryItemResponse:
        item = await InventoryRepository.get_item(tenant_id, item_id)
        if item is None:
            raise NotFoundError("Inventory item not found")
        return InventoryService._item_response(item)

    @staticmethod
    async def create_item(tenant_id: str, data: InventoryItemCreate, actor_id: str) -> InventoryItemResponse:
        existing = await InventoryRepository.get_by_sku(tenant_id, data.sku)
        if existing:
            raise ConflictError(f"SKU '{data.sku}' already exists")
        item = await InventoryRepository.create_item(tenant_id, data.model_dump())
        await InventoryService._index(item)
        await AuditService.log_event(tenant_id, "inventory.created", "inventory_item", str(item.id), actor_id)
        return InventoryService._item_response(item)

    @staticmethod
    async def update_item(
        tenant_id: str, item_id: str, data: InventoryItemUpdate, actor_id: str
    ) -> InventoryItemResponse:
        item = await InventoryRepository.get_item(tenant_id, item_id)
        if item is None:
            raise NotFoundError("Inventory item not found")
        item = await InventoryRepository.update_item(item, data.model_dump(exclude_unset=True))
        await InventoryService._index(item)
        await AuditService.log_event(tenant_id, "inventory.updated", "inventory_item", str(item.id), actor_id)
        return InventoryService._item_response(item)

    @staticmethod
    async def delete_item(tenant_id: str, item_id: str, actor_id: str) -> None:
        item = await InventoryRepository.get_item(tenant_id, item_id)
        if item is None:
            raise NotFoundError("Inventory item not found")
        await InventoryRepository.soft_delete_item(item)
        await AuditService.log_event(tenant_id, "inventory.deleted", "inventory_item", str(item.id), actor_id)

    @staticmethod
    async def list_movements(tenant_id: str, item_id: str | None = None) -> list[InventoryMovementResponse]:
        movements = await InventoryRepository.list_movements(tenant_id, item_id)
        return [
            InventoryMovementResponse(
                id=str(m.id),
                item_id=str(m.item_id),
                movement_type=m.movement_type,
                quantity=m.quantity,
                reference=m.reference,
                notes=m.notes,
                performed_by=str(m.performed_by),
            )
            for m in movements
        ]

    @staticmethod
    async def record_movement(
        tenant_id: str, data: InventoryMovementCreate, actor_id: str
    ) -> InventoryMovementResponse:
        item = await InventoryRepository.get_item(tenant_id, data.item_id)
        if item is None:
            raise NotFoundError("Inventory item not found")

        if data.movement_type not in ("in", "out", "adjust"):
            raise ValidationError("movement_type must be in, out, or adjust")

        delta = data.quantity
        if data.movement_type == "out":
            delta = -abs(data.quantity)
        elif data.movement_type == "in":
            delta = abs(data.quantity)
        elif data.movement_type == "adjust":
            item.quantity = data.quantity
            await item.touch()
            delta = 0

        if data.movement_type != "adjust":
            new_qty = item.quantity + delta
            if new_qty < 0:
                raise ValidationError("Insufficient stock")
            item.quantity = new_qty
            await item.touch()

        movement = await InventoryRepository.create_movement(
            tenant_id,
            {
                "item_id": PydanticObjectId(data.item_id),
                "movement_type": data.movement_type,
                "quantity": data.quantity,
                "reference": data.reference,
                "notes": data.notes,
                "performed_by": PydanticObjectId(actor_id),
            },
        )
        await InventoryService._index(item)
        await AuditService.log_event(
            tenant_id, "inventory.movement", "inventory_movement", str(movement.id), actor_id
        )
        return InventoryMovementResponse(
            id=str(movement.id),
            item_id=str(movement.item_id),
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            reference=movement.reference,
            notes=movement.notes,
            performed_by=str(movement.performed_by),
        )
