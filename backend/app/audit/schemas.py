from typing import Any

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any]
    ip_address: str | None
    request_id: str | None
    created_at: str


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int


class AuditLogQuery(BaseModel):
    resource_type: str | None = None
    user_id: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    skip: int = Field(default=0, ge=0)
