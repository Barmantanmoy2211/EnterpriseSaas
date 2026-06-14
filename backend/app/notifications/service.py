from beanie import PydanticObjectId

from app.notifications.models import Notification
from app.notifications.repository import NotificationRepository
from app.notifications.schemas import NotificationCreate, NotificationResponse


class NotificationService:
    @staticmethod
    def _to_response(n: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=str(n.id),
            user_id=str(n.user_id),
            title=n.title,
            body=n.body,
            notification_type=n.notification_type,
            is_read=n.is_read,
            link=n.link,
            metadata=n.metadata,
            created_at=n.created_at.isoformat(),
        )

    @staticmethod
    async def send(
        tenant_id: str,
        data: NotificationCreate,
        actor_id: str | None = None,
    ) -> NotificationResponse:
        from app.audit.service import AuditService

        notification = await NotificationRepository.create(
            tenant_id,
            {
                "user_id": PydanticObjectId(data.user_id),
                "title": data.title,
                "body": data.body,
                "notification_type": data.notification_type,
                "link": data.link,
                "metadata": data.metadata,
            },
        )

        if data.send_email:
            from app.notifications.tasks import send_email_notification

            send_email_notification.delay(
                tenant_id=tenant_id,
                user_id=data.user_id,
                subject=data.title,
                body=data.body,
            )

        await AuditService.log_event(
            tenant_id=tenant_id,
            action="notification.sent",
            resource_type="notification",
            resource_id=str(notification.id),
            user_id=actor_id,
            details={"recipient_id": data.user_id, "type": data.notification_type},
        )

        return NotificationService._to_response(notification)

    @staticmethod
    async def notify_user(
        tenant_id: str,
        user_id: str,
        title: str,
        body: str,
        notification_type: str = "info",
        link: str | None = None,
        metadata: dict | None = None,
        send_email: bool = False,
    ) -> NotificationResponse:
        return await NotificationService.send(
            tenant_id,
            NotificationCreate(
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                link=link,
                metadata=metadata or {},
                send_email=send_email,
            ),
        )

    @staticmethod
    async def list_for_user(
        tenant_id: str,
        user_id: str,
        unread_only: bool = False,
    ) -> tuple[list[NotificationResponse], int]:
        items = await NotificationRepository.list_for_user(tenant_id, user_id, unread_only)
        unread = await NotificationRepository.count_unread(tenant_id, user_id)
        return [NotificationService._to_response(n) for n in items], unread

    @staticmethod
    async def mark_read(tenant_id: str, user_id: str, notification_id: str) -> NotificationResponse:
        from app.shared.exceptions import ForbiddenError, NotFoundError

        notification = await NotificationRepository.get_by_id(tenant_id, notification_id)
        if notification is None:
            raise NotFoundError("Notification not found")
        if str(notification.user_id) != user_id:
            raise ForbiddenError("Cannot access this notification")
        updated = await NotificationRepository.mark_read(notification)
        return NotificationService._to_response(updated)

    @staticmethod
    async def mark_all_read(tenant_id: str, user_id: str) -> int:
        return await NotificationRepository.mark_all_read(tenant_id, user_id)
