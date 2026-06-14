from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.resource.schemas import (
    AllocationCreate,
    AllocationResponse,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from app.resource.service import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/allocations", response_model=list[AllocationResponse])
async def list_allocations(
    resource_id: str | None = Query(None),
    user=Depends(require_permission("resource", "read")),
):
    return await ResourceService.list_allocations(str(user.tenant_id), resource_id)


@router.post("/allocations", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation(
    data: AllocationCreate,
    user=Depends(require_permission("resource", "manage")),
):
    return await ResourceService.create_allocation(str(user.tenant_id), data, str(user.id))


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    resource_type: str | None = Query(None),
    user=Depends(require_permission("resource", "read")),
):
    return await ResourceService.list_resources(str(user.tenant_id), resource_type)


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: str, user=Depends(require_permission("resource", "read"))):
    return await ResourceService.get_resource(str(user.tenant_id), resource_id)


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreate,
    user=Depends(require_permission("resource", "manage")),
):
    return await ResourceService.create_resource(str(user.tenant_id), data, str(user.id))


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    data: ResourceUpdate,
    user=Depends(require_permission("resource", "manage")),
):
    return await ResourceService.update_resource(str(user.tenant_id), resource_id, data, str(user.id))


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    user=Depends(require_permission("resource", "manage")),
):
    await ResourceService.delete_resource(str(user.tenant_id), resource_id, str(user.id))
