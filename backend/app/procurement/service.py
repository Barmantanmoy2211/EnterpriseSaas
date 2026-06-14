from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.procurement.models import PurchaseOrder
from app.procurement.repository import ProcurementRepository
from app.procurement.schemas import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderUpdate,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError


def _calc_total(lines: list) -> float:
    return sum(line.quantity * line.unit_price for line in lines)


class ProcurementService:
    @staticmethod
    def _supplier_response(supplier) -> SupplierResponse:
        return SupplierResponse(
            id=str(supplier.id),
            name=supplier.name,
            code=supplier.code,
            contact_name=supplier.contact_name,
            contact_email=supplier.contact_email,
            contact_phone=supplier.contact_phone,
            status=supplier.status,
            metadata=supplier.metadata,
        )

    @staticmethod
    def _order_response(order: PurchaseOrder) -> PurchaseOrderResponse:
        return PurchaseOrderResponse(
            id=str(order.id),
            po_number=order.po_number,
            supplier_id=str(order.supplier_id),
            status=order.status,
            lines=order.lines,
            total_amount=order.total_amount,
            currency=order.currency,
            requested_by=str(order.requested_by),
            expected_delivery=order.expected_delivery,
            notes=order.notes,
            metadata=order.metadata,
        )

    @staticmethod
    async def list_suppliers(tenant_id: str, status: str | None = None) -> list[SupplierResponse]:
        suppliers = await ProcurementRepository.list_suppliers(tenant_id, status)
        return [ProcurementService._supplier_response(s) for s in suppliers]

    @staticmethod
    async def get_supplier(tenant_id: str, supplier_id: str) -> SupplierResponse:
        supplier = await ProcurementRepository.get_supplier(tenant_id, supplier_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")
        return ProcurementService._supplier_response(supplier)

    @staticmethod
    async def create_supplier(tenant_id: str, data: SupplierCreate, actor_id: str) -> SupplierResponse:
        supplier = await ProcurementRepository.create_supplier(tenant_id, data.model_dump())
        await SearchRepository.upsert(
            tenant_id, "supplier", str(supplier.id), supplier.name, supplier.contact_email, [supplier.code], {}
        )
        await AuditService.log_event(tenant_id, "procurement.supplier_created", "supplier", str(supplier.id), actor_id)
        return ProcurementService._supplier_response(supplier)

    @staticmethod
    async def update_supplier(
        tenant_id: str, supplier_id: str, data: SupplierUpdate, actor_id: str
    ) -> SupplierResponse:
        supplier = await ProcurementRepository.get_supplier(tenant_id, supplier_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")
        supplier = await ProcurementRepository.update_supplier(supplier, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "procurement.supplier_updated", "supplier", str(supplier.id), actor_id)
        return ProcurementService._supplier_response(supplier)

    @staticmethod
    async def delete_supplier(tenant_id: str, supplier_id: str, actor_id: str) -> None:
        supplier = await ProcurementRepository.get_supplier(tenant_id, supplier_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")
        await ProcurementRepository.soft_delete_supplier(supplier)
        await AuditService.log_event(tenant_id, "procurement.supplier_deleted", "supplier", str(supplier.id), actor_id)

    @staticmethod
    async def list_orders(tenant_id: str, status: str | None = None) -> list[PurchaseOrderResponse]:
        orders = await ProcurementRepository.list_orders(tenant_id, status)
        return [ProcurementService._order_response(o) for o in orders]

    @staticmethod
    async def get_order(tenant_id: str, order_id: str) -> PurchaseOrderResponse:
        order = await ProcurementRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Purchase order not found")
        return ProcurementService._order_response(order)

    @staticmethod
    async def create_order(tenant_id: str, data: PurchaseOrderCreate, actor_id: str) -> PurchaseOrderResponse:
        existing = await ProcurementRepository.get_order_by_number(tenant_id, data.po_number)
        if existing:
            raise ConflictError(f"PO number '{data.po_number}' already exists")

        supplier = await ProcurementRepository.get_supplier(tenant_id, data.supplier_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")

        payload = data.model_dump(exclude={"supplier_id", "lines"})
        payload["supplier_id"] = PydanticObjectId(data.supplier_id)
        payload["requested_by"] = PydanticObjectId(actor_id)
        payload["lines"] = data.lines
        payload["total_amount"] = _calc_total(data.lines)

        order = await ProcurementRepository.create_order(tenant_id, payload)
        await AuditService.log_event(tenant_id, "procurement.order_created", "purchase_order", str(order.id), actor_id)
        return ProcurementService._order_response(order)

    @staticmethod
    async def update_order(
        tenant_id: str, order_id: str, data: PurchaseOrderUpdate, actor_id: str
    ) -> PurchaseOrderResponse:
        order = await ProcurementRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Purchase order not found")

        updates = data.model_dump(exclude_unset=True)
        if data.lines is not None:
            updates["total_amount"] = _calc_total(data.lines)

        order = await ProcurementRepository.update_order(order, updates)
        await AuditService.log_event(tenant_id, "procurement.order_updated", "purchase_order", str(order.id), actor_id)
        return ProcurementService._order_response(order)

    @staticmethod
    async def delete_order(tenant_id: str, order_id: str, actor_id: str) -> None:
        order = await ProcurementRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Purchase order not found")
        await ProcurementRepository.soft_delete_order(order)
        await AuditService.log_event(tenant_id, "procurement.order_deleted", "purchase_order", str(order.id), actor_id)
