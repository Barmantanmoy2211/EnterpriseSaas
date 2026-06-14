from fastapi import APIRouter, Depends, Query, status

from app.logistics.schemas import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from app.logistics.service import LogisticsService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.get("/shipments", response_model=list[ShipmentResponse])
async def list_shipments(
    status: str | None = Query(None),
    user=Depends(require_permission("logistics", "read")),
):
    return await LogisticsService.list_shipments(str(user.tenant_id), status)


@router.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(shipment_id: str, user=Depends(require_permission("logistics", "read"))):
    return await LogisticsService.get_shipment(str(user.tenant_id), shipment_id)


@router.post("/shipments", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    data: ShipmentCreate,
    user=Depends(require_permission("logistics", "manage")),
):
    return await LogisticsService.create_shipment(str(user.tenant_id), data, str(user.id))


@router.patch("/shipments/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: str,
    data: ShipmentUpdate,
    user=Depends(require_permission("logistics", "manage")),
):
    return await LogisticsService.update_shipment(str(user.tenant_id), shipment_id, data, str(user.id))


@router.delete("/shipments/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: str,
    user=Depends(require_permission("logistics", "manage")),
):
    await LogisticsService.delete_shipment(str(user.tenant_id), shipment_id, str(user.id))
