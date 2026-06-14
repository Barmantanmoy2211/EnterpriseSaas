from datetime import datetime

from beanie import PydanticObjectId

from app.calendar.models import CalendarEvent


class CalendarRepository:
    @staticmethod
    async def list_events(
        tenant_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        organizer_id: str | None = None,
    ) -> list[CalendarEvent]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if organizer_id:
            filt["organizer_id"] = PydanticObjectId(organizer_id)
        if start and end:
            filt["start_at"] = {"$gte": start}
            filt["end_at"] = {"$lte": end}
        elif start:
            filt["start_at"] = {"$gte": start}
        return await CalendarEvent.find(filt).sort("+start_at").to_list()

    @staticmethod
    async def get(tenant_id: str, event_id: str) -> CalendarEvent | None:
        event = await CalendarEvent.get(event_id)
        if event and str(event.tenant_id) == tenant_id and not event.is_deleted:
            return event
        return None

    @staticmethod
    async def create(tenant_id: str, data: dict) -> CalendarEvent:
        event = CalendarEvent(tenant_id=PydanticObjectId(tenant_id), **data)
        await event.insert()
        return event

    @staticmethod
    async def update(event: CalendarEvent, data: dict) -> CalendarEvent:
        for key, value in data.items():
            if value is not None:
                setattr(event, key, value)
        await event.touch()
        return event

    @staticmethod
    async def soft_delete(event: CalendarEvent) -> None:
        await event.soft_delete()
