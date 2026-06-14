from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.notifications.schemas import NotificationCreate, NotificationListResponse, NotificationResponse
from app.notifications.service import NotificationService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False),
    user=Depends(get_current_user),
):
    items, unread = await NotificationService.list_for_user(
        str(user.tenant_id), str(user.id), unread_only
    )
    return NotificationListResponse(items=items, unread_count=unread)


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    user=Depends(require_permission("notification", "manage")),
):
    return await NotificationService.send(str(user.tenant_id), data, actor_id=str(user.id))


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(notification_id: str, user=Depends(get_current_user)):
    return await NotificationService.mark_read(
        str(user.tenant_id), str(user.id), notification_id
    )


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(user=Depends(get_current_user)):
    await NotificationService.mark_all_read(str(user.tenant_id), str(user.id))
