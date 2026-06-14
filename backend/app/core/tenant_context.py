from contextvars import ContextVar

tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)
tenant_slug_var: ContextVar[str | None] = ContextVar("tenant_slug", default=None)


def get_current_tenant_id() -> str | None:
    return tenant_id_var.get()


def set_tenant_context(tenant_id: str | None, tenant_slug: str | None = None) -> None:
    tenant_id_var.set(tenant_id)
    tenant_slug_var.set(tenant_slug)
