from beanie import PydanticObjectId

from app.inventory.models import InventoryItem, InventoryMovement


class InventoryRepository:
    @staticmethod
    async def list_items(tenant_id: str, status: str | None = None) -> list[InventoryItem]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await InventoryItem.find(filt).sort("+name").to_list()

    @staticmethod
    async def get_item(tenant_id: str, item_id: str) -> InventoryItem | None:
        item = await InventoryItem.get(item_id)
        if item and str(item.tenant_id) == tenant_id and not item.is_deleted:
            return item
        return None

    @staticmethod
    async def get_by_sku(tenant_id: str, sku: str) -> InventoryItem | None:
        return await InventoryItem.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "sku": sku, "is_deleted": False}
        )

    @staticmethod
    async def create_item(tenant_id: str, data: dict) -> InventoryItem:
        item = InventoryItem(tenant_id=PydanticObjectId(tenant_id), **data)
        await item.insert()
        return item

    @staticmethod
    async def update_item(item: InventoryItem, data: dict) -> InventoryItem:
        for key, value in data.items():
            if value is not None:
                setattr(item, key, value)
        await item.touch()
        return item

    @staticmethod
    async def soft_delete_item(item: InventoryItem) -> None:
        await item.soft_delete()

    @staticmethod
    async def list_movements(tenant_id: str, item_id: str | None = None) -> list[InventoryMovement]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if item_id:
            filt["item_id"] = PydanticObjectId(item_id)
        return await InventoryMovement.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def create_movement(tenant_id: str, data: dict) -> InventoryMovement:
        movement = InventoryMovement(tenant_id=PydanticObjectId(tenant_id), **data)
        await movement.insert()
        return movement
