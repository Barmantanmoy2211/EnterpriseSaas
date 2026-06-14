from datetime import UTC, datetime
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import Field


class Tenant(Document):
    slug: str
    name: str
    status: str = "active"
    plan: str = "starter"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "tenants"
        indexes = [
            [("slug", 1)],
            [("status", 1)],
        ]


class TenantSettings(Document):
    tenant_id: PydanticObjectId
    branding: dict[str, Any] = Field(default_factory=lambda: {"primary_color": "#2563eb"})
    auth_policy: dict[str, Any] = Field(default_factory=dict)
    org_defaults: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "tenant_settings"
        indexes = [[("tenant_id", 1)]]
