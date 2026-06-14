from beanie import PydanticObjectId

from app.procurement.models import PurchaseOrder, Supplier


class ProcurementRepository:
    @staticmethod
    async def list_suppliers(tenant_id: str, status: str | None = None) -> list[Supplier]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await Supplier.find(filt).sort("+name").to_list()

    @staticmethod
    async def get_supplier(tenant_id: str, supplier_id: str) -> Supplier | None:
        supplier = await Supplier.get(supplier_id)
        if supplier and str(supplier.tenant_id) == tenant_id and not supplier.is_deleted:
            return supplier
        return None

    @staticmethod
    async def create_supplier(tenant_id: str, data: dict) -> Supplier:
        supplier = Supplier(tenant_id=PydanticObjectId(tenant_id), **data)
        await supplier.insert()
        return supplier

    @staticmethod
    async def update_supplier(supplier: Supplier, data: dict) -> Supplier:
        for key, value in data.items():
            if value is not None:
                setattr(supplier, key, value)
        await supplier.touch()
        return supplier

    @staticmethod
    async def soft_delete_supplier(supplier: Supplier) -> None:
        await supplier.soft_delete()

    @staticmethod
    async def list_orders(tenant_id: str, status: str | None = None) -> list[PurchaseOrder]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await PurchaseOrder.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_order(tenant_id: str, order_id: str) -> PurchaseOrder | None:
        order = await PurchaseOrder.get(order_id)
        if order and str(order.tenant_id) == tenant_id and not order.is_deleted:
            return order
        return None

    @staticmethod
    async def get_order_by_number(tenant_id: str, po_number: str) -> PurchaseOrder | None:
        return await PurchaseOrder.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "po_number": po_number, "is_deleted": False}
        )

    @staticmethod
    async def create_order(tenant_id: str, data: dict) -> PurchaseOrder:
        order = PurchaseOrder(tenant_id=PydanticObjectId(tenant_id), **data)
        await order.insert()
        return order

    @staticmethod
    async def update_order(order: PurchaseOrder, data: dict) -> PurchaseOrder:
        for key, value in data.items():
            if value is not None:
                setattr(order, key, value)
        await order.touch()
        return order

    @staticmethod
    async def soft_delete_order(order: PurchaseOrder) -> None:
        await order.soft_delete()
