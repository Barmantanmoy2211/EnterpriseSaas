from typing import Any

from beanie import PydanticObjectId

from app.permissions.models import Permission
from app.permissions.repository import SYSTEM_PERMISSIONS, PermissionRepository
from app.permissions.schemas import (
    PermissionResponse,
    RoleAssignmentCreate,
    RoleAssignmentResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.shared.exceptions import ConflictError, ForbiddenError, NotFoundError


class PermissionService:
    @staticmethod
    async def seed_tenant_defaults(tenant_id: str, admin_user_id: str) -> None:
        perm_ids: list[PydanticObjectId] = []
        for resource, action, description in SYSTEM_PERMISSIONS:
            existing = await PermissionRepository.get_permission(tenant_id, resource, action)
            if existing:
                perm_ids.append(existing.id)
            else:
                perm = await PermissionRepository.create_permission(
                    tenant_id, resource, action, description
                )
                perm_ids.append(perm.id)

        admin_role = await PermissionRepository.get_role_by_code(tenant_id, "tenant_admin")
        if admin_role is None:
            admin_role = await PermissionRepository.create_role(
                tenant_id,
                {
                    "code": "tenant_admin",
                    "name": "Tenant Administrator",
                    "description": "Full access to tenant resources",
                    "is_system": True,
                    "permission_ids": perm_ids,
                },
            )
            await PermissionRepository.create_assignment(
                tenant_id,
                {
                    "user_id": PydanticObjectId(admin_user_id),
                    "role_id": admin_role.id,
                    "scope_node_id": None,
                },
            )

        from app.shared.hr_seed import seed_hr_defaults
        from app.shared.ops_seed import seed_ops_defaults

        await seed_hr_defaults(tenant_id, admin_user_id)
        await seed_ops_defaults(tenant_id, admin_user_id)

    @staticmethod
    def _perm_response(p: Permission) -> PermissionResponse:
        return PermissionResponse(
            id=str(p.id),
            resource=p.resource,
            action=p.action,
            description=p.description,
            conditions=p.conditions,
        )

    @staticmethod
    def _role_response(r) -> RoleResponse:
        return RoleResponse(
            id=str(r.id),
            code=r.code,
            name=r.name,
            description=r.description,
            is_system=r.is_system,
            permission_ids=[str(pid) for pid in r.permission_ids],
        )

    @staticmethod
    async def list_permissions(tenant_id: str) -> list[PermissionResponse]:
        perms = await PermissionRepository.list_permissions(tenant_id)
        return [PermissionService._perm_response(p) for p in perms]

    @staticmethod
    async def list_roles(tenant_id: str) -> list[RoleResponse]:
        roles = await PermissionRepository.list_roles(tenant_id)
        return [PermissionService._role_response(r) for r in roles]

    @staticmethod
    async def create_role(tenant_id: str, data: RoleCreate) -> RoleResponse:
        existing = await PermissionRepository.get_role_by_code(tenant_id, data.code)
        if existing:
            raise ConflictError(f"Role '{data.code}' already exists")
        role_data = data.model_dump()
        role_data["permission_ids"] = [PydanticObjectId(pid) for pid in data.permission_ids]
        role = await PermissionRepository.create_role(tenant_id, role_data)
        return PermissionService._role_response(role)

    @staticmethod
    async def update_role(tenant_id: str, role_id: str, data: RoleUpdate) -> RoleResponse:
        role = await PermissionRepository.get_role(tenant_id, role_id)
        if role is None:
            raise NotFoundError("Role not found")
        if role.is_system and data.permission_ids is not None:
            raise ForbiddenError("Cannot modify permissions of system role via API")
        update_data = data.model_dump(exclude_unset=True)
        if "permission_ids" in update_data and update_data["permission_ids"] is not None:
            update_data["permission_ids"] = [
                PydanticObjectId(pid) for pid in update_data["permission_ids"]
            ]
        updated = await PermissionRepository.update_role(role, update_data)
        return PermissionService._role_response(updated)

    @staticmethod
    async def list_assignments(tenant_id: str) -> list[RoleAssignmentResponse]:
        assignments = await PermissionRepository.list_assignments(tenant_id)
        return [
            RoleAssignmentResponse(
                id=str(a.id),
                user_id=str(a.user_id),
                role_id=str(a.role_id),
                scope_node_id=str(a.scope_node_id) if a.scope_node_id else None,
            )
            for a in assignments
        ]

    @staticmethod
    async def create_assignment(tenant_id: str, data: RoleAssignmentCreate) -> RoleAssignmentResponse:
        role = await PermissionRepository.get_role(tenant_id, data.role_id)
        if role is None:
            raise NotFoundError("Role not found")
        assignment = await PermissionRepository.create_assignment(
            tenant_id,
            {
                "user_id": PydanticObjectId(data.user_id),
                "role_id": PydanticObjectId(data.role_id),
                "scope_node_id": PydanticObjectId(data.scope_node_id)
                if data.scope_node_id
                else None,
            },
        )
        return RoleAssignmentResponse(
            id=str(assignment.id),
            user_id=str(assignment.user_id),
            role_id=str(assignment.role_id),
            scope_node_id=str(assignment.scope_node_id) if assignment.scope_node_id else None,
        )

    @staticmethod
    async def delete_assignment(tenant_id: str, assignment_id: str) -> None:
        from app.permissions.models import RoleAssignment

        assignment = await RoleAssignment.get(assignment_id)
        if assignment is None or str(assignment.tenant_id) != tenant_id:
            raise NotFoundError("Assignment not found")
        await PermissionRepository.delete_assignment(assignment)

    @staticmethod
    async def user_has_permission(
        tenant_id: str,
        user_id: str,
        resource: str,
        action: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        permissions = await PermissionRepository.get_permissions_for_user(tenant_id, user_id)
        for perm in permissions:
            if perm.resource == resource and perm.action == action:
                if perm.conditions and context:
                    if not PermissionService._evaluate_conditions(perm.conditions, context):
                        continue
                return True
        return False

    @staticmethod
    def _evaluate_conditions(conditions: dict[str, Any], context: dict[str, Any]) -> bool:
        for key, expected in conditions.items():
            if context.get(key) != expected:
                return False
        return True
