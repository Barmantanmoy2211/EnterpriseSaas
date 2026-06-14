from datetime import datetime
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class CalendarEvent(TenantDocument):
    title: str
    description: str = ""
    start_at: datetime
    end_at: datetime
    organizer_id: PydanticObjectId
    attendee_ids: list[PydanticObjectId] = Field(default_factory=list)
    location: str = ""
    all_day: bool = False
    related_entity_type: str = ""
    related_entity_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "calendar_events"
        indexes = [
            [("tenant_id", 1), ("start_at", 1)],
            [("tenant_id", 1), ("organizer_id", 1)],
        ]
