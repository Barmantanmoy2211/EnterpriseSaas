from datetime import datetime

from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.calendar.models import CalendarEvent
from app.calendar.repository import CalendarRepository
from app.calendar.schemas import CalendarEventCreate, CalendarEventResponse, CalendarEventUpdate
from app.shared.exceptions import NotFoundError


class CalendarService:
    @staticmethod
    def _response(event: CalendarEvent) -> CalendarEventResponse:
        return CalendarEventResponse(
            id=str(event.id),
            title=event.title,
            description=event.description,
            start_at=event.start_at,
            end_at=event.end_at,
            organizer_id=str(event.organizer_id),
            attendee_ids=[str(a) for a in event.attendee_ids],
            location=event.location,
            all_day=event.all_day,
            related_entity_type=event.related_entity_type,
            related_entity_id=event.related_entity_id,
            metadata=event.metadata,
        )

    @staticmethod
    async def list_events(
        tenant_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        organizer_id: str | None = None,
    ) -> list[CalendarEventResponse]:
        events = await CalendarRepository.list_events(tenant_id, start, end, organizer_id)
        return [CalendarService._response(e) for e in events]

    @staticmethod
    async def get_event(tenant_id: str, event_id: str) -> CalendarEventResponse:
        event = await CalendarRepository.get(tenant_id, event_id)
        if event is None:
            raise NotFoundError("Calendar event not found")
        return CalendarService._response(event)

    @staticmethod
    async def create_event(
        tenant_id: str, data: CalendarEventCreate, actor_id: str
    ) -> CalendarEventResponse:
        payload = data.model_dump(exclude={"attendee_ids"})
        payload["organizer_id"] = PydanticObjectId(actor_id)
        payload["attendee_ids"] = [PydanticObjectId(a) for a in data.attendee_ids]

        event = await CalendarRepository.create(tenant_id, payload)
        await AuditService.log_event(tenant_id, "calendar.created", "calendar_event", str(event.id), actor_id)
        return CalendarService._response(event)

    @staticmethod
    async def update_event(
        tenant_id: str, event_id: str, data: CalendarEventUpdate, actor_id: str
    ) -> CalendarEventResponse:
        event = await CalendarRepository.get(tenant_id, event_id)
        if event is None:
            raise NotFoundError("Calendar event not found")

        updates = data.model_dump(exclude_unset=True, exclude={"attendee_ids"})
        if data.attendee_ids is not None:
            updates["attendee_ids"] = [PydanticObjectId(a) for a in data.attendee_ids]

        event = await CalendarRepository.update(event, updates)
        await AuditService.log_event(tenant_id, "calendar.updated", "calendar_event", str(event.id), actor_id)
        return CalendarService._response(event)

    @staticmethod
    async def delete_event(tenant_id: str, event_id: str, actor_id: str) -> None:
        event = await CalendarRepository.get(tenant_id, event_id)
        if event is None:
            raise NotFoundError("Calendar event not found")
        await CalendarRepository.soft_delete(event)
        await AuditService.log_event(tenant_id, "calendar.deleted", "calendar_event", str(event.id), actor_id)
