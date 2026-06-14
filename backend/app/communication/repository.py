from beanie import PydanticObjectId

from app.communication.models import CommunicationMessage


class CommunicationRepository:
    @staticmethod
    async def list_messages(
        tenant_id: str,
        message_type: str | None = None,
        channel: str | None = None,
        sender_id: str | None = None,
    ) -> list[CommunicationMessage]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if message_type:
            filt["message_type"] = message_type
        if channel:
            filt["channel"] = channel
        if sender_id:
            filt["sender_id"] = PydanticObjectId(sender_id)
        return await CommunicationMessage.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get(tenant_id: str, message_id: str) -> CommunicationMessage | None:
        msg = await CommunicationMessage.get(message_id)
        if msg and str(msg.tenant_id) == tenant_id and not msg.is_deleted:
            return msg
        return None

    @staticmethod
    async def create(tenant_id: str, data: dict) -> CommunicationMessage:
        msg = CommunicationMessage(tenant_id=PydanticObjectId(tenant_id), **data)
        await msg.insert()
        return msg

    @staticmethod
    async def update(msg: CommunicationMessage, data: dict) -> CommunicationMessage:
        for key, value in data.items():
            if value is not None:
                setattr(msg, key, value)
        await msg.touch()
        return msg

    @staticmethod
    async def soft_delete(msg: CommunicationMessage) -> None:
        await msg.soft_delete()
