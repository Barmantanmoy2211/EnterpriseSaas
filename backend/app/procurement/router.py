from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.procurement.schemas import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderUpdate,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.procurement.service import ProcurementService

router = APIRouter(prefix="/procurement", tags=["procurement"])


@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    status: str | None = Query(None),
    user=Depends(require_permission("procurement", "read")),
):
    return await ProcurementService.list_suppliers(str(user.tenant_id), status)


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str, user=Depends(require_permission("procurement", "read"))):
    return await ProcurementService.get_supplier(str(user.tenant_id), supplier_id)


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    user=Depends(require_permission("procurement", "manage")),
):
    return await ProcurementService.create_supplier(str(user.tenant_id), data, str(user.id))


@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    user=Depends(require_permission("procurement", "manage")),
):
    return await ProcurementService.update_supplier(str(user.tenant_id), supplier_id, data, str(user.id))


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: str,
    user=Depends(require_permission("procurement", "manage")),
):
    await ProcurementService.delete_supplier(str(user.tenant_id), supplier_id, str(user.id))


@router.get("/orders", response_model=list[PurchaseOrderResponse])
async def list_orders(
    status: str | None = Query(None),
    user=Depends(require_permission("procurement", "read")),
):
    return await ProcurementService.list_orders(str(user.tenant_id), status)


@router.get("/orders/{order_id}", response_model=PurchaseOrderResponse)
async def get_order(order_id: str, user=Depends(require_permission("procurement", "read"))):
    return await ProcurementService.get_order(str(user.tenant_id), order_id)


@router.post("/orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: PurchaseOrderCreate,
    user=Depends(require_permission("procurement", "manage")),
):
    return await ProcurementService.create_order(str(user.tenant_id), data, str(user.id))


@router.patch("/orders/{order_id}", response_model=PurchaseOrderResponse)
async def update_order(
    order_id: str,
    data: PurchaseOrderUpdate,
    user=Depends(require_permission("procurement", "manage")),
):
    return await ProcurementService.update_order(str(user.tenant_id), order_id, data, str(user.id))


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    user=Depends(require_permission("procurement", "manage")),
):
    await ProcurementService.delete_order(str(user.tenant_id), order_id, str(user.id))
