from typing import Any

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., max_length=2000)
    notification_type: str = "info"
    link: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    send_email: bool = False


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    notification_type: str
    is_read: bool
    link: str | None
    metadata: dict[str, Any]
    created_at: str


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int
