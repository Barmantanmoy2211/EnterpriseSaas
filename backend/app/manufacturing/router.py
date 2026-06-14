from fastapi import APIRouter, Depends, Query, status

from app.manufacturing.schemas import (
    BomCreate,
    BomResponse,
    BomUpdate,
    ProductionOrderCreate,
    ProductionOrderResponse,
    ProductionOrderUpdate,
)
from app.manufacturing.service import ManufacturingService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])


@router.get("/boms", response_model=list[BomResponse])
async def list_boms(user=Depends(require_permission("manufacturing", "read"))):
    return await ManufacturingService.list_boms(str(user.tenant_id))


@router.get("/boms/{bom_id}", response_model=BomResponse)
async def get_bom(bom_id: str, user=Depends(require_permission("manufacturing", "read"))):
    return await ManufacturingService.get_bom(str(user.tenant_id), bom_id)


@router.post("/boms", response_model=BomResponse, status_code=status.HTTP_201_CREATED)
async def create_bom(
    data: BomCreate,
    user=Depends(require_permission("manufacturing", "manage")),
):
    return await ManufacturingService.create_bom(str(user.tenant_id), data, str(user.id))


@router.patch("/boms/{bom_id}", response_model=BomResponse)
async def update_bom(
    bom_id: str,
    data: BomUpdate,
    user=Depends(require_permission("manufacturing", "manage")),
):
    return await ManufacturingService.update_bom(str(user.tenant_id), bom_id, data, str(user.id))


@router.delete("/boms/{bom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bom(
    bom_id: str,
    user=Depends(require_permission("manufacturing", "manage")),
):
    await ManufacturingService.delete_bom(str(user.tenant_id), bom_id, str(user.id))


@router.get("/orders", response_model=list[ProductionOrderResponse])
async def list_production_orders(
    status: str | None = Query(None),
    user=Depends(require_permission("manufacturing", "read")),
):
    return await ManufacturingService.list_orders(str(user.tenant_id), status)


@router.get("/orders/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(
    order_id: str,
    user=Depends(require_permission("manufacturing", "read")),
):
    return await ManufacturingService.get_order(str(user.tenant_id), order_id)


@router.post("/orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    data: ProductionOrderCreate,
    user=Depends(require_permission("manufacturing", "manage")),
):
    return await ManufacturingService.create_order(str(user.tenant_id), data, str(user.id))


@router.patch("/orders/{order_id}", response_model=ProductionOrderResponse)
async def update_production_order(
    order_id: str,
    data: ProductionOrderUpdate,
    user=Depends(require_permission("manufacturing", "manage")),
):
    return await ManufacturingService.update_order(str(user.tenant_id), order_id, data, str(user.id))


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_order(
    order_id: str,
    user=Depends(require_permission("manufacturing", "manage")),
):
    await ManufacturingService.delete_order(str(user.tenant_id), order_id, str(user.id))
