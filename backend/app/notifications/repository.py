from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.notifications.models import Notification


class NotificationRepository:
    @staticmethod
    async def create(tenant_id: str, data: dict) -> Notification:
        notification = Notification(tenant_id=PydanticObjectId(tenant_id), **data)
        await notification.insert()
        return notification

    @staticmethod
    async def list_for_user(
        tenant_id: str,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        filt: dict = {
            "tenant_id": PydanticObjectId(tenant_id),
            "user_id": PydanticObjectId(user_id),
            "is_deleted": False,
        }
        if unread_only:
            filt["is_read"] = False
        return (
            await Notification.find(filt).sort("-created_at").limit(limit).to_list()
        )

    @staticmethod
    async def count_unread(tenant_id: str, user_id: str) -> int:
        return await Notification.find(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "user_id": PydanticObjectId(user_id),
                "is_read": False,
                "is_deleted": False,
            }
        ).count()

    @staticmethod
    async def get_by_id(tenant_id: str, notification_id: str) -> Notification | None:
        n = await Notification.get(notification_id)
        if n and str(n.tenant_id) == tenant_id and not n.is_deleted:
            return n
        return None

    @staticmethod
    async def mark_read(notification: Notification) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        await notification.touch()
        return notification

    @staticmethod
    async def mark_all_read(tenant_id: str, user_id: str) -> int:
        notifications = await NotificationRepository.list_for_user(
            tenant_id, user_id, unread_only=True, limit=500
        )
        for n in notifications:
            n.is_read = True
            n.read_at = datetime.now(UTC)
            await n.touch()
        return len(notifications)
