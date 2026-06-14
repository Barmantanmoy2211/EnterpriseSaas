from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.organization.schemas import (
    OrgNodeCreate,
    OrgNodeMove,
    OrgNodeResponse,
    OrgNodeTypeCreate,
    OrgNodeTypeResponse,
    OrgNodeTypeUpdate,
    OrgNodeUpdate,
)
from app.organization.service import OrganizationService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("/node-types", response_model=list[OrgNodeTypeResponse])
async def list_node_types(user=Depends(get_current_user)):
    return await OrganizationService.list_node_types(str(user.tenant_id))


@router.post("/node-types", response_model=OrgNodeTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_node_type(
    data: OrgNodeTypeCreate,
    user=Depends(require_permission("org", "manage_types")),
):
    return await OrganizationService.create_node_type(str(user.tenant_id), data)


@router.patch("/node-types/{type_id}", response_model=OrgNodeTypeResponse)
async def update_node_type(
    type_id: str,
    data: OrgNodeTypeUpdate,
    user=Depends(require_permission("org", "manage_types")),
):
    return await OrganizationService.update_node_type(str(user.tenant_id), type_id, data)


@router.delete("/node-types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node_type(
    type_id: str,
    user=Depends(require_permission("org", "manage_types")),
):
    await OrganizationService.delete_node_type(str(user.tenant_id), type_id)


@router.get("/nodes/tree", response_model=list[OrgNodeResponse])
async def get_org_tree(user=Depends(get_current_user)):
    return await OrganizationService.get_tree(str(user.tenant_id))


@router.post("/seed-defaults", status_code=status.HTTP_201_CREATED)
async def seed_organization_defaults(
    user=Depends(require_permission("org", "manage_types")),
):
    from app.shared.org_seed import seed_org_defaults

    await seed_org_defaults(str(user.tenant_id))
    return {"status": "ok", "message": "Default hierarchy levels created"}


@router.post("/nodes", response_model=OrgNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    data: OrgNodeCreate,
    user=Depends(require_permission("org", "create")),
):
    return await OrganizationService.create_node(str(user.tenant_id), data)


@router.patch("/nodes/{node_id}", response_model=OrgNodeResponse)
async def update_node(
    node_id: str,
    data: OrgNodeUpdate,
    user=Depends(require_permission("org", "update")),
):
    return await OrganizationService.update_node(str(user.tenant_id), node_id, data)


@router.post("/nodes/{node_id}/move", response_model=OrgNodeResponse)
async def move_node(
    node_id: str,
    data: OrgNodeMove,
    user=Depends(require_permission("org", "update")),
):
    return await OrganizationService.move_node(str(user.tenant_id), node_id, data)


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: str,
    user=Depends(require_permission("org", "delete")),
):
    await OrganizationService.delete_node(str(user.tenant_id), node_id)
