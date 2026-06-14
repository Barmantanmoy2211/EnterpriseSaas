from beanie import PydanticObjectId

from app.manufacturing.models import BillOfMaterials, ProductionOrder


class ManufacturingRepository:
    @staticmethod
    async def list_boms(tenant_id: str) -> list[BillOfMaterials]:
        return await BillOfMaterials.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).sort("+product_sku").to_list()

    @staticmethod
    async def get_bom(tenant_id: str, bom_id: str) -> BillOfMaterials | None:
        bom = await BillOfMaterials.get(bom_id)
        if bom and str(bom.tenant_id) == tenant_id and not bom.is_deleted:
            return bom
        return None

    @staticmethod
    async def get_bom_by_sku(tenant_id: str, product_sku: str) -> BillOfMaterials | None:
        return await BillOfMaterials.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "product_sku": product_sku, "is_deleted": False}
        )

    @staticmethod
    async def create_bom(tenant_id: str, data: dict) -> BillOfMaterials:
        bom = BillOfMaterials(tenant_id=PydanticObjectId(tenant_id), **data)
        await bom.insert()
        return bom

    @staticmethod
    async def update_bom(bom: BillOfMaterials, data: dict) -> BillOfMaterials:
        for key, value in data.items():
            if value is not None:
                setattr(bom, key, value)
        await bom.touch()
        return bom

    @staticmethod
    async def soft_delete_bom(bom: BillOfMaterials) -> None:
        await bom.soft_delete()

    @staticmethod
    async def list_orders(tenant_id: str, status: str | None = None) -> list[ProductionOrder]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await ProductionOrder.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_order(tenant_id: str, order_id: str) -> ProductionOrder | None:
        order = await ProductionOrder.get(order_id)
        if order and str(order.tenant_id) == tenant_id and not order.is_deleted:
            return order
        return None

    @staticmethod
    async def get_order_by_number(tenant_id: str, order_number: str) -> ProductionOrder | None:
        return await ProductionOrder.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "order_number": order_number, "is_deleted": False}
        )

    @staticmethod
    async def create_order(tenant_id: str, data: dict) -> ProductionOrder:
        order = ProductionOrder(tenant_id=PydanticObjectId(tenant_id), **data)
        await order.insert()
        return order

    @staticmethod
    async def update_order(order: ProductionOrder, data: dict) -> ProductionOrder:
        for key, value in data.items():
            if value is not None:
                setattr(order, key, value)
        await order.touch()
        return order

    @staticmethod
    async def soft_delete_order(order: ProductionOrder) -> None:
        await order.soft_delete()
