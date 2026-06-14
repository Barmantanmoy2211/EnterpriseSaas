from beanie import PydanticObjectId

from app.logistics.models import Shipment


class LogisticsRepository:
    @staticmethod
    async def list_shipments(tenant_id: str, status: str | None = None) -> list[Shipment]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await Shipment.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_shipment(tenant_id: str, shipment_id: str) -> Shipment | None:
        shipment = await Shipment.get(shipment_id)
        if shipment and str(shipment.tenant_id) == tenant_id and not shipment.is_deleted:
            return shipment
        return None

    @staticmethod
    async def get_by_number(tenant_id: str, shipment_number: str) -> Shipment | None:
        return await Shipment.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "shipment_number": shipment_number, "is_deleted": False}
        )

    @staticmethod
    async def create_shipment(tenant_id: str, data: dict) -> Shipment:
        shipment = Shipment(tenant_id=PydanticObjectId(tenant_id), **data)
        await shipment.insert()
        return shipment

    @staticmethod
    async def update_shipment(shipment: Shipment, data: dict) -> Shipment:
        for key, value in data.items():
            if value is not None:
                setattr(shipment, key, value)
        await shipment.touch()
        return shipment

    @staticmethod
    async def soft_delete_shipment(shipment: Shipment) -> None:
        await shipment.soft_delete()
