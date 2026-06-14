from fastapi import APIRouter, Depends, Query, status

from app.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryMovementCreate,
    InventoryMovementResponse,
)
from app.inventory.service import InventoryService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/items", response_model=list[InventoryItemResponse])
async def list_items(
    status: str | None = Query(None),
    user=Depends(require_permission("inventory", "read")),
):
    return await InventoryService.list_items(str(user.tenant_id), status)


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_item(item_id: str, user=Depends(require_permission("inventory", "read"))):
    return await InventoryService.get_item(str(user.tenant_id), item_id)


@router.post("/items", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: InventoryItemCreate,
    user=Depends(require_permission("inventory", "manage")),
):
    return await InventoryService.create_item(str(user.tenant_id), data, str(user.id))


@router.patch("/items/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    item_id: str,
    data: InventoryItemUpdate,
    user=Depends(require_permission("inventory", "manage")),
):
    return await InventoryService.update_item(str(user.tenant_id), item_id, data, str(user.id))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    user=Depends(require_permission("inventory", "manage")),
):
    await InventoryService.delete_item(str(user.tenant_id), item_id, str(user.id))


@router.get("/movements", response_model=list[InventoryMovementResponse])
async def list_movements(
    item_id: str | None = Query(None),
    user=Depends(require_permission("inventory", "read")),
):
    return await InventoryService.list_movements(str(user.tenant_id), item_id)


@router.post("/movements", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED)
async def record_movement(
    data: InventoryMovementCreate,
    user=Depends(require_permission("inventory", "manage")),
):
    return await InventoryService.record_movement(str(user.tenant_id), data, str(user.id))
