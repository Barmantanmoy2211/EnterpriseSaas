from typing import Any

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    message_type: str = "announcement"
    subject: str
    body: str
    recipient_id: str | None = None
    channel: str = "general"
    is_pinned: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None
    is_pinned: bool | None = None
    metadata: dict[str, Any] | None = None


class MessageResponse(BaseModel):
    id: str
    message_type: str
    subject: str
    body: str
    sender_id: str
    recipient_id: str | None
    channel: str
    is_pinned: bool
    read_by: list[str]
    created_at: str
    metadata: dict[str, Any]
