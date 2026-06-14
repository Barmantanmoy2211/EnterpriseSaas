from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CalendarEventCreate(BaseModel):
    title: str
    description: str = ""
    start_at: datetime
    end_at: datetime
    attendee_ids: list[str] = Field(default_factory=list)
    location: str = ""
    all_day: bool = False
    related_entity_type: str = ""
    related_entity_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarEventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    attendee_ids: list[str] | None = None
    location: str | None = None
    all_day: bool | None = None
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    metadata: dict[str, Any] | None = None


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    organizer_id: str
    attendee_ids: list[str]
    location: str
    all_day: bool
    related_entity_type: str
    related_entity_id: str
    metadata: dict[str, Any]
