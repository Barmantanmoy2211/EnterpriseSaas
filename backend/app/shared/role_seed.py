"""Seed default role templates for new tenants."""

from beanie import PydanticObjectId

from app.permissions.repository import PermissionRepository

# (resource, action) — use "*" for all actions on that resource
ROLE_TEMPLATES: list[dict] = [
    {
        "code": "hr_manager",
        "name": "HR Manager",
        "description": "Full access to HR modules",
        "permissions": [
            ("employee", "*"),
            ("recruitment", "*"),
            ("attendance", "*"),
            ("leave", "*"),
            ("performance", "*"),
            ("training", "*"),
            ("onboarding", "*"),
            ("exit", "*"),
            ("notification", "read"),
            ("search", "read"),
        ],
    },
    {
        "code": "operations_manager",
        "name": "Operations Manager",
        "description": "Projects, tasks, calendar, documents, and reports",
        "permissions": [
            ("project", "*"),
            ("task", "*"),
            ("calendar", "*"),
            ("document", "*"),
            ("communication", "*"),
            ("report", "*"),
            ("analytics", "read"),
            ("notification", "read"),
            ("search", "read"),
        ],
    },
    {
        "code": "enterprise_manager",
        "name": "Enterprise Manager",
        "description": "Inventory, finance, procurement, manufacturing, logistics",
        "permissions": [
            ("inventory", "*"),
            ("resource", "*"),
            ("finance", "*"),
            ("procurement", "*"),
            ("manufacturing", "*"),
            ("logistics", "*"),
            ("notification", "read"),
            ("search", "read"),
        ],
    },
    {
        "code": "manager",
        "name": "Manager",
        "description": "Read access plus approvals and leave requests",
        "permissions": [
            ("org", "read"),
            ("employee", "read"),
            ("project", "read"),
            ("task", "read"),
            ("leave", "read"),
            ("leave", "request"),
            ("leave", "manage"),
            ("attendance", "read"),
            ("approval", "read"),
            ("approval", "action"),
            ("notification", "read"),
            ("search", "read"),
            ("calendar", "read"),
            ("calendar", "manage"),
        ],
    },
    {
        "code": "employee",
        "name": "Employee",
        "description": "Standard employee self-service access",
        "permissions": [
            ("org", "read"),
            ("employee", "read"),
            ("leave", "read"),
            ("leave", "request"),
            ("attendance", "read"),
            ("attendance", "manage"),
            ("performance", "read"),
            ("training", "read"),
            ("onboarding", "read"),
            ("task", "read"),
            ("calendar", "read"),
            ("notification", "read"),
            ("search", "read"),
            ("communication", "read"),
        ],
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
        for (resource, action), perm_id in perm_index.items():
            if action in ("read", "request") and perm_id not in seen:
                ids.append(perm_id)
                seen.add(perm_id)
        return ids

    ids = []
    seen: set[PydanticObjectId] = set()
    for resource, action in spec:
        if action == "*":
            for (r, a), perm_id in perm_index.items():
                if r == resource and perm_id not in seen:
                    ids.append(perm_id)
                    seen.add(perm_id)
        else:
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
