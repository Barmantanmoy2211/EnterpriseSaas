from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.logistics.models import Shipment
from app.logistics.repository import LogisticsRepository
from app.logistics.schemas import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError


class LogisticsService:
    @staticmethod
    def _response(shipment: Shipment) -> ShipmentResponse:
        return ShipmentResponse(
            id=str(shipment.id),
            shipment_number=shipment.shipment_number,
            origin=shipment.origin,
            destination=shipment.destination,
            carrier=shipment.carrier,
            tracking_number=shipment.tracking_number,
            status=shipment.status,
            items=shipment.items,
            scheduled_date=shipment.scheduled_date,
            delivered_date=shipment.delivered_date,
            created_by=str(shipment.created_by),
            purchase_order_id=str(shipment.purchase_order_id) if shipment.purchase_order_id else None,
            metadata=shipment.metadata,
        )

    @staticmethod
    async def list_shipments(tenant_id: str, status: str | None = None) -> list[ShipmentResponse]:
        shipments = await LogisticsRepository.list_shipments(tenant_id, status)
        return [LogisticsService._response(s) for s in shipments]

    @staticmethod
    async def get_shipment(tenant_id: str, shipment_id: str) -> ShipmentResponse:
        shipment = await LogisticsRepository.get_shipment(tenant_id, shipment_id)
        if shipment is None:
            raise NotFoundError("Shipment not found")
        return LogisticsService._response(shipment)

    @staticmethod
    async def create_shipment(tenant_id: str, data: ShipmentCreate, actor_id: str) -> ShipmentResponse:
        existing = await LogisticsRepository.get_by_number(tenant_id, data.shipment_number)
        if existing:
            raise ConflictError(f"Shipment number '{data.shipment_number}' already exists")

        payload = data.model_dump(exclude={"purchase_order_id"})
        payload["created_by"] = PydanticObjectId(actor_id)
        if data.purchase_order_id:
            payload["purchase_order_id"] = PydanticObjectId(data.purchase_order_id)

        shipment = await LogisticsRepository.create_shipment(tenant_id, payload)
        await SearchRepository.upsert(
            tenant_id,
            "shipment",
            str(shipment.id),
            shipment.shipment_number,
            f"{shipment.origin} → {shipment.destination}",
            [shipment.tracking_number, shipment.carrier],
            {"status": shipment.status},
        )
        await AuditService.log_event(tenant_id, "logistics.created", "shipment", str(shipment.id), actor_id)
        return LogisticsService._response(shipment)

    @staticmethod
    async def update_shipment(
        tenant_id: str, shipment_id: str, data: ShipmentUpdate, actor_id: str
    ) -> ShipmentResponse:
        shipment = await LogisticsRepository.get_shipment(tenant_id, shipment_id)
        if shipment is None:
            raise NotFoundError("Shipment not found")
        shipment = await LogisticsRepository.update_shipment(shipment, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "logistics.updated", "shipment", str(shipment.id), actor_id)
        return LogisticsService._response(shipment)

    @staticmethod
    async def delete_shipment(tenant_id: str, shipment_id: str, actor_id: str) -> None:
        shipment = await LogisticsRepository.get_shipment(tenant_id, shipment_id)
        if shipment is None:
            raise NotFoundError("Shipment not found")
        await LogisticsRepository.soft_delete_shipment(shipment)
        await AuditService.log_event(tenant_id, "logistics.deleted", "shipment", str(shipment.id), actor_id)
