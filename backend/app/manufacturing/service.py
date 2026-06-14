from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.manufacturing.models import BillOfMaterials, ProductionOrder
from app.manufacturing.repository import ManufacturingRepository
from app.manufacturing.schemas import (
    BomCreate,
    BomResponse,
    BomUpdate,
    ProductionOrderCreate,
    ProductionOrderResponse,
    ProductionOrderUpdate,
)
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError


class ManufacturingService:
    @staticmethod
    def _bom_response(bom: BillOfMaterials) -> BomResponse:
        return BomResponse(
            id=str(bom.id),
            product_sku=bom.product_sku,
            name=bom.name,
            description=bom.description,
            components=bom.components,
            version=bom.version,
            is_active=bom.is_active,
            metadata=bom.metadata,
        )

    @staticmethod
    def _order_response(order: ProductionOrder) -> ProductionOrderResponse:
        return ProductionOrderResponse(
            id=str(order.id),
            order_number=order.order_number,
            bom_id=str(order.bom_id),
            quantity=order.quantity,
            status=order.status,
            scheduled_start=order.scheduled_start,
            scheduled_end=order.scheduled_end,
            created_by=str(order.created_by),
            notes=order.notes,
            metadata=order.metadata,
        )

    @staticmethod
    async def list_boms(tenant_id: str) -> list[BomResponse]:
        boms = await ManufacturingRepository.list_boms(tenant_id)
        return [ManufacturingService._bom_response(b) for b in boms]

    @staticmethod
    async def get_bom(tenant_id: str, bom_id: str) -> BomResponse:
        bom = await ManufacturingRepository.get_bom(tenant_id, bom_id)
        if bom is None:
            raise NotFoundError("Bill of materials not found")
        return ManufacturingService._bom_response(bom)

    @staticmethod
    async def create_bom(tenant_id: str, data: BomCreate, actor_id: str) -> BomResponse:
        existing = await ManufacturingRepository.get_bom_by_sku(tenant_id, data.product_sku)
        if existing:
            raise ConflictError(f"BOM for SKU '{data.product_sku}' already exists")
        bom = await ManufacturingRepository.create_bom(tenant_id, data.model_dump())
        await SearchRepository.upsert(
            tenant_id, "bom", str(bom.id), bom.name, bom.product_sku, [bom.product_sku], {}
        )
        await AuditService.log_event(tenant_id, "manufacturing.bom_created", "bom", str(bom.id), actor_id)
        return ManufacturingService._bom_response(bom)

    @staticmethod
    async def update_bom(tenant_id: str, bom_id: str, data: BomUpdate, actor_id: str) -> BomResponse:
        bom = await ManufacturingRepository.get_bom(tenant_id, bom_id)
        if bom is None:
            raise NotFoundError("Bill of materials not found")
        bom = await ManufacturingRepository.update_bom(bom, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "manufacturing.bom_updated", "bom", str(bom.id), actor_id)
        return ManufacturingService._bom_response(bom)

    @staticmethod
    async def delete_bom(tenant_id: str, bom_id: str, actor_id: str) -> None:
        bom = await ManufacturingRepository.get_bom(tenant_id, bom_id)
        if bom is None:
            raise NotFoundError("Bill of materials not found")
        await ManufacturingRepository.soft_delete_bom(bom)
        await AuditService.log_event(tenant_id, "manufacturing.bom_deleted", "bom", str(bom.id), actor_id)

    @staticmethod
    async def list_orders(tenant_id: str, status: str | None = None) -> list[ProductionOrderResponse]:
        orders = await ManufacturingRepository.list_orders(tenant_id, status)
        return [ManufacturingService._order_response(o) for o in orders]

    @staticmethod
    async def get_order(tenant_id: str, order_id: str) -> ProductionOrderResponse:
        order = await ManufacturingRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Production order not found")
        return ManufacturingService._order_response(order)

    @staticmethod
    async def create_order(
        tenant_id: str, data: ProductionOrderCreate, actor_id: str
    ) -> ProductionOrderResponse:
        existing = await ManufacturingRepository.get_order_by_number(tenant_id, data.order_number)
        if existing:
            raise ConflictError(f"Order number '{data.order_number}' already exists")

        bom = await ManufacturingRepository.get_bom(tenant_id, data.bom_id)
        if bom is None:
            raise NotFoundError("Bill of materials not found")

        payload = data.model_dump(exclude={"bom_id"})
        payload["bom_id"] = PydanticObjectId(data.bom_id)
        payload["created_by"] = PydanticObjectId(actor_id)

        order = await ManufacturingRepository.create_order(tenant_id, payload)
        await AuditService.log_event(
            tenant_id, "manufacturing.order_created", "production_order", str(order.id), actor_id
        )
        return ManufacturingService._order_response(order)

    @staticmethod
    async def update_order(
        tenant_id: str, order_id: str, data: ProductionOrderUpdate, actor_id: str
    ) -> ProductionOrderResponse:
        order = await ManufacturingRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Production order not found")
        order = await ManufacturingRepository.update_order(order, data.model_dump(exclude_unset=True))
        await AuditService.log_event(
            tenant_id, "manufacturing.order_updated", "production_order", str(order.id), actor_id
        )
        return ManufacturingService._order_response(order)

    @staticmethod
    async def delete_order(tenant_id: str, order_id: str, actor_id: str) -> None:
        order = await ManufacturingRepository.get_order(tenant_id, order_id)
        if order is None:
            raise NotFoundError("Production order not found")
        await ManufacturingRepository.soft_delete_order(order)
        await AuditService.log_event(
            tenant_id, "manufacturing.order_deleted", "production_order", str(order.id), actor_id
        )
