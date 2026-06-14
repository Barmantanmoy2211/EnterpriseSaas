from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class CommunicationMessage(TenantDocument):
    message_type: str = "announcement"
    subject: str
    body: str
    sender_id: PydanticObjectId
    recipient_id: PydanticObjectId | None = None
    channel: str = "general"
    is_pinned: bool = False
    read_by: list[PydanticObjectId] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "communication_messages"
        indexes = [
            [("tenant_id", 1), ("message_type", 1)],
            [("tenant_id", 1), ("channel", 1)],
            [("tenant_id", 1), ("sender_id", 1)],
        ]
