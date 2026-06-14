from beanie import PydanticObjectId

from app.permissions.models import Permission, Role, RoleAssignment

SYSTEM_PERMISSIONS = [
    ("org", "read", "View organization structure"),
    ("org", "create", "Create organization nodes"),
    ("org", "update", "Update organization nodes"),
    ("org", "delete", "Delete organization nodes"),
    ("org", "manage_types", "Manage organization node types"),
    ("user", "read", "View users"),
    ("user", "manage", "Manage users"),
    ("role", "read", "View roles"),
    ("role", "manage", "Manage roles and assignments"),
    ("tenant", "settings", "Manage tenant settings"),
    ("audit", "read", "View audit logs"),
    ("notification", "read", "View notifications"),
    ("notification", "manage", "Send notifications"),
    ("workflow", "read", "View workflows"),
    ("workflow", "manage", "Manage workflows and instances"),
    ("approval", "read", "View all approvals"),
    ("approval", "action", "Approve or reject requests"),
    ("search", "read", "Use global search"),
    ("search", "manage", "Manage search index"),
]


class PermissionRepository:
    @staticmethod
    async def list_permissions(tenant_id: str) -> list[Permission]:
        return await Permission.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def get_permission(tenant_id: str, resource: str, action: str) -> Permission | None:
        return await Permission.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "resource": resource,
                "action": action,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create_permission(
        tenant_id: str, resource: str, action: str, description: str
    ) -> Permission:
        perm = Permission(
            tenant_id=PydanticObjectId(tenant_id),
            resource=resource,
            action=action,
            description=description,
        )
        await perm.insert()
        return perm

    @staticmethod
    async def list_roles(tenant_id: str) -> list[Role]:
        return await Role.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def get_role(tenant_id: str, role_id: str) -> Role | None:
        role = await Role.get(role_id)
        if role and str(role.tenant_id) == tenant_id and not role.is_deleted:
            return role
        return None

    @staticmethod
    async def get_role_by_code(tenant_id: str, code: str) -> Role | None:
        return await Role.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "code": code,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create_role(tenant_id: str, data: dict) -> Role:
        role = Role(tenant_id=PydanticObjectId(tenant_id), **data)
        await role.insert()
        return role

    @staticmethod
    async def update_role(role: Role, data: dict) -> Role:
        for key, value in data.items():
            if value is not None:
                setattr(role, key, value)
        await role.touch()
        return role

    @staticmethod
    async def list_assignments(tenant_id: str, user_id: str | None = None) -> list[RoleAssignment]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if user_id:
            filt["user_id"] = PydanticObjectId(user_id)
        return await RoleAssignment.find(filt).to_list()

    @staticmethod
    async def create_assignment(tenant_id: str, data: dict) -> RoleAssignment:
        assignment = RoleAssignment(tenant_id=PydanticObjectId(tenant_id), **data)
        await assignment.insert()
        return assignment

    @staticmethod
    async def delete_assignment(assignment: RoleAssignment) -> None:
        await assignment.soft_delete()

    @staticmethod
    async def get_permissions_for_user(tenant_id: str, user_id: str) -> list[Permission]:
        assignments = await PermissionRepository.list_assignments(tenant_id, user_id)
        if not assignments:
            return []

        role_ids = [a.role_id for a in assignments]
        roles = await Role.find({"_id": {"$in": role_ids}, "is_deleted": False}).to_list()

        perm_ids: set[PydanticObjectId] = set()
        for role in roles:
            perm_ids.update(role.permission_ids)

        if not perm_ids:
            return []

        return await Permission.find({"_id": {"$in": list(perm_ids)}, "is_deleted": False}).to_list()
