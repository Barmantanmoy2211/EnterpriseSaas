from datetime import UTC, datetime
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import Field


class AuditLog(Document):
    """Immutable audit trail — no updates or soft deletes."""

    tenant_id: PydanticObjectId
    user_id: PydanticObjectId | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None
    request_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "audit_logs"
        indexes = [
            [("tenant_id", 1), ("created_at", -1)],
            [("tenant_id", 1), ("resource_type", 1), ("resource_id", 1)],
            [("tenant_id", 1), ("user_id", 1)],
        ]
