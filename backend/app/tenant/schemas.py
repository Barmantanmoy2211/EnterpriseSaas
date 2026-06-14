from typing import Any

from pydantic import BaseModel, Field


class TenantResponse(BaseModel):
    id: str
    slug: str
    name: str
    status: str
    plan: str

    model_config = {"from_attributes": True}


class TenantUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)


class TenantSettingsResponse(BaseModel):
    branding: dict[str, Any]
    auth_policy: dict[str, Any]
    org_defaults: dict[str, Any]


class TenantSettingsUpdateRequest(BaseModel):
    branding: dict[str, Any] | None = None
    auth_policy: dict[str, Any] | None = None
    org_defaults: dict[str, Any] | None = None
