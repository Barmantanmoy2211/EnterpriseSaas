"""Seed default organization hierarchy types for new tenants."""

from app.organization.repository import OrganizationRepository

DEFAULT_NODE_TYPES = [
    {
        "code": "company",
        "label": "Company",
        "is_root_allowed": True,
        "allowed_child_types": ["division", "department"],
        "type_schema": {},
    },
    {
        "code": "division",
        "label": "Division",
        "is_root_allowed": False,
        "allowed_child_types": ["department", "team"],
        "type_schema": {},
    },
    {
        "code": "department",
        "label": "Department",
        "is_root_allowed": False,
        "allowed_child_types": ["team"],
        "type_schema": {},
    },
    {
        "code": "team",
        "label": "Team",
        "is_root_allowed": False,
        "allowed_child_types": [],
        "type_schema": {},
    },
]


async def seed_org_defaults(tenant_id: str) -> None:
    existing = await OrganizationRepository.list_node_types(tenant_id)
    if existing:
        return

    for node_type in DEFAULT_NODE_TYPES:
        await OrganizationRepository.create_node_type(tenant_id, node_type)
