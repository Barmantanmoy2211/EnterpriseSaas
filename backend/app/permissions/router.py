from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.permissions.dependencies import require_permission
from app.permissions.schemas import (
    PermissionResponse,
    RoleAssignmentCreate,
    RoleAssignmentResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.permissions.service import PermissionService

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(user=Depends(get_current_user)):
    return await PermissionService.list_permissions(str(user.tenant_id))


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(user=Depends(get_current_user)):
    return await PermissionService.list_roles(str(user.tenant_id))


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    user=Depends(require_permission("role", "manage")),
):
    return await PermissionService.create_role(str(user.tenant_id), data)


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    user=Depends(require_permission("role", "manage")),
):
    return await PermissionService.update_role(str(user.tenant_id), role_id, data)


@router.get("/assignments", response_model=list[RoleAssignmentResponse])
async def list_assignments(user=Depends(require_permission("role", "read"))):
    return await PermissionService.list_assignments(str(user.tenant_id))


@router.post("/assignments", response_model=RoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: RoleAssignmentCreate,
    user=Depends(require_permission("role", "manage")),
):
    return await PermissionService.create_assignment(str(user.tenant_id), data)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: str,
    user=Depends(require_permission("role", "manage")),
):
    await PermissionService.delete_assignment(str(user.tenant_id), assignment_id)
