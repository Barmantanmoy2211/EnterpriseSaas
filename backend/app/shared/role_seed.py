"""Seed default role templates for new tenants."""

from beanie import PydanticObjectId

from app.permissions.repository import PermissionRepository
from app.shared.permission_modules import PERMISSION_MODULES

# Standard write bundle per module for manager-style roles
_WRITE = ("create", "update", "edit")


def _module_perms(resource: str, actions: tuple[str, ...]) -> list[tuple[str, str]]:
    return [(resource, action) for action in actions]


ROLE_TEMPLATES: list[dict] = [
    {
        "code": "hr_manager",
        "name": "HR Manager",
        "description": "Full access to HR modules",
        "permissions": (
            _module_perms("employee", ("read", *_WRITE))
            + _module_perms("recruitment", ("read", *_WRITE))
            + _module_perms("attendance", ("read", *_WRITE))
            + _module_perms("leave", ("read", "request", *_WRITE))
            + _module_perms("performance", ("read", *_WRITE))
            + _module_perms("training", ("read", *_WRITE))
            + _module_perms("onboarding", ("read", *_WRITE))
            + _module_perms("exit", ("read", *_WRITE))
            + _module_perms("notification", ("read",))
            + _module_perms("search", ("read",))
        ),
    },
    {
        "code": "operations_manager",
        "name": "Operations Manager",
        "description": "Projects, tasks, calendar, documents, and reports",
        "permissions": (
            _module_perms("project", ("read", *_WRITE))
            + _module_perms("task", ("read", *_WRITE))
            + _module_perms("calendar", ("read", *_WRITE))
            + _module_perms("document", ("read", *_WRITE))
            + _module_perms("communication", ("read", *_WRITE))
            + _module_perms("report", ("read", *_WRITE))
            + _module_perms("analytics", ("read",))
            + _module_perms("notification", ("read",))
            + _module_perms("search", ("read",))
        ),
    },
    {
        "code": "enterprise_manager",
        "name": "Enterprise Manager",
        "description": "Inventory, finance, procurement, manufacturing, logistics",
        "permissions": (
            _module_perms("inventory", ("read", *_WRITE))
            + _module_perms("resource", ("read", *_WRITE))
            + _module_perms("finance", ("read", *_WRITE))
            + _module_perms("procurement", ("read", *_WRITE))
            + _module_perms("manufacturing", ("read", *_WRITE))
            + _module_perms("logistics", ("read", *_WRITE))
            + _module_perms("notification", ("read",))
            + _module_perms("search", ("read",))
        ),
    },
    {
        "code": "manager",
        "name": "Manager",
        "description": "Read access plus approvals and leave requests",
        "permissions": (
            _module_perms("org", ("read",))
            + _module_perms("employee", ("read",))
            + _module_perms("project", ("read",))
            + _module_perms("task", ("read",))
            + _module_perms("leave", ("read", "request", "update"))
            + _module_perms("attendance", ("read",))
            + _module_perms("approval", ("read", "action"))
            + _module_perms("notification", ("read",))
            + _module_perms("search", ("read",))
            + _module_perms("calendar", ("read", "update"))
        ),
    },
    {
        "code": "employee",
        "name": "Employee",
        "description": "Standard employee self-service access",
        "permissions": (
            _module_perms("org", ("read",))
            + _module_perms("employee", ("read",))
            + _module_perms("leave", ("read", "request"))
            + _module_perms("attendance", ("read", "update"))
            + _module_perms("performance", ("read",))
            + _module_perms("training", ("read",))
            + _module_perms("onboarding", ("read",))
            + _module_perms("task", ("read",))
            + _module_perms("calendar", ("read",))
            + _module_perms("notification", ("read",))
            + _module_perms("search", ("read",))
            + _module_perms("communication", ("read",))
        ),
    },
    {
        "code": "viewer",
        "name": "Viewer",
        "description": "Read-only access across modules",
        "permissions": "read_only",
    },
]


def _resolve_permission_ids(
    spec: list[tuple[str, str]] | str,
    perm_index: dict[tuple[str, str], PydanticObjectId],
) -> list[PydanticObjectId]:
    if spec == "read_only":
        ids: list[PydanticObjectId] = []
        seen: set[PydanticObjectId] = set()
        for resource, _label in PERMISSION_MODULES:
            perm_id = perm_index.get((resource, "read"))
            if perm_id and perm_id not in seen:
                ids.append(perm_id)
                seen.add(perm_id)
        for (resource, action), perm_id in perm_index.items():
            if action == "request" and perm_id not in seen:
                ids.append(perm_id)
                seen.add(perm_id)
        return ids

    ids = []
    seen: set[PydanticObjectId] = set()
    for resource, action in spec:
        perm_id = perm_index.get((resource, action))
        if perm_id and perm_id not in seen:
            ids.append(perm_id)
            seen.add(perm_id)
    return ids


async def seed_default_roles(tenant_id: str) -> None:
    perms = await PermissionRepository.list_permissions(tenant_id)
    perm_index = {(p.resource, p.action): p.id for p in perms}

    for template in ROLE_TEMPLATES:
        existing = await PermissionRepository.get_role_by_code(tenant_id, template["code"])
        if existing:
            continue

        permission_ids = _resolve_permission_ids(template["permissions"], perm_index)
        await PermissionRepository.create_role(
            tenant_id,
            {
                "code": template["code"],
                "name": template["name"],
                "description": template["description"],
                "is_system": True,
                "permission_ids": permission_ids,
            },
        )
