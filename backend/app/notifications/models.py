from datetime import datetime
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Notification(TenantDocument):
    user_id: PydanticObjectId
    title: str
    body: str
    notification_type: str = "info"
    is_read: bool = False
    link: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    read_at: datetime | None = None

    class Settings:
        name = "notifications"
        indexes = [
            [("tenant_id", 1), ("user_id", 1), ("is_read", 1)],
            [("tenant_id", 1), ("created_at", -1)],
        ]
