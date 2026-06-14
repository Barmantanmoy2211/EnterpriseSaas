from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.calendar.schemas import CalendarEventCreate, CalendarEventResponse, CalendarEventUpdate
from app.calendar.service import CalendarService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/calendar/events", tags=["calendar"])


@router.get("", response_model=list[CalendarEventResponse])
async def list_events(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    organizer_id: str | None = Query(None),
    user=Depends(require_permission("calendar", "read")),
):
    return await CalendarService.list_events(str(user.tenant_id), start, end, organizer_id)


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(event_id: str, user=Depends(require_permission("calendar", "read"))):
    return await CalendarService.get_event(str(user.tenant_id), event_id)


@router.post("", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: CalendarEventCreate,
    user=Depends(require_permission("calendar", "manage")),
):
    return await CalendarService.create_event(str(user.tenant_id), data, str(user.id))


@router.patch("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    data: CalendarEventUpdate,
    user=Depends(require_permission("calendar", "manage")),
):
    return await CalendarService.update_event(str(user.tenant_id), event_id, data, str(user.id))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    user=Depends(require_permission("calendar", "manage")),
):
    await CalendarService.delete_event(str(user.tenant_id), event_id, str(user.id))
