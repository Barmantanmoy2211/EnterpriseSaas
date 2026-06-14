"""Seed default organization hierarchy types for new tenants — disabled; tenants define their own."""

async def seed_org_defaults(tenant_id: str) -> None:
    """No-op: hierarchy level types are created by the tenant during onboarding."""
    del tenant_id
