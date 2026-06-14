from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.communication.models import CommunicationMessage
from app.communication.repository import CommunicationRepository
from app.communication.schemas import MessageCreate, MessageResponse, MessageUpdate
from app.notifications.service import NotificationService
from app.shared.exceptions import NotFoundError


class CommunicationService:
    @staticmethod
    def _response(msg: CommunicationMessage) -> MessageResponse:
        return MessageResponse(
            id=str(msg.id),
            message_type=msg.message_type,
            subject=msg.subject,
            body=msg.body,
            sender_id=str(msg.sender_id),
            recipient_id=str(msg.recipient_id) if msg.recipient_id else None,
            channel=msg.channel,
            is_pinned=msg.is_pinned,
            read_by=[str(r) for r in msg.read_by],
            created_at=msg.created_at.isoformat(),
            metadata=msg.metadata,
        )

    @staticmethod
    async def list_messages(
        tenant_id: str,
        message_type: str | None = None,
        channel: str | None = None,
        sender_id: str | None = None,
    ) -> list[MessageResponse]:
        messages = await CommunicationRepository.list_messages(
            tenant_id, message_type, channel, sender_id
        )
        return [CommunicationService._response(m) for m in messages]

    @staticmethod
    async def get_message(tenant_id: str, message_id: str) -> MessageResponse:
        msg = await CommunicationRepository.get(tenant_id, message_id)
        if msg is None:
            raise NotFoundError("Message not found")
        return CommunicationService._response(msg)

    @staticmethod
    async def create_message(tenant_id: str, data: MessageCreate, actor_id: str) -> MessageResponse:
        payload = data.model_dump(exclude={"recipient_id"})
        payload["sender_id"] = PydanticObjectId(actor_id)
        if data.recipient_id:
            payload["recipient_id"] = PydanticObjectId(data.recipient_id)

        msg = await CommunicationRepository.create(tenant_id, payload)
        await AuditService.log_event(tenant_id, "communication.created", "message", str(msg.id), actor_id)

        if data.recipient_id:
            await NotificationService.notify_user(
                tenant_id,
                data.recipient_id,
                "New message",
                data.subject,
                metadata={"message_id": str(msg.id), "type": data.message_type},
            )

        return CommunicationService._response(msg)

    @staticmethod
    async def update_message(
        tenant_id: str, message_id: str, data: MessageUpdate, actor_id: str
    ) -> MessageResponse:
        msg = await CommunicationRepository.get(tenant_id, message_id)
        if msg is None:
            raise NotFoundError("Message not found")

        msg = await CommunicationRepository.update(msg, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "communication.updated", "message", str(msg.id), actor_id)
        return CommunicationService._response(msg)

    @staticmethod
    async def mark_read(tenant_id: str, message_id: str, actor_id: str) -> MessageResponse:
        msg = await CommunicationRepository.get(tenant_id, message_id)
        if msg is None:
            raise NotFoundError("Message not found")

        user_oid = PydanticObjectId(actor_id)
        if user_oid not in msg.read_by:
            msg.read_by.append(user_oid)
            await msg.touch()

        return CommunicationService._response(msg)

    @staticmethod
    async def delete_message(tenant_id: str, message_id: str, actor_id: str) -> None:
        msg = await CommunicationRepository.get(tenant_id, message_id)
        if msg is None:
            raise NotFoundError("Message not found")
        await CommunicationRepository.soft_delete(msg)
        await AuditService.log_event(tenant_id, "communication.deleted", "message", str(msg.id), actor_id)
