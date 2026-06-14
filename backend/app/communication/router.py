from fastapi import APIRouter, Depends, Query, status

from app.communication.schemas import MessageCreate, MessageResponse, MessageUpdate
from app.communication.service import CommunicationService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/communication", tags=["communication"])


@router.get("/messages", response_model=list[MessageResponse])
async def list_messages(
    message_type: str | None = Query(None),
    channel: str | None = Query(None),
    sender_id: str | None = Query(None),
    user=Depends(require_permission("communication", "read")),
):
    return await CommunicationService.list_messages(
        str(user.tenant_id), message_type, channel, sender_id
    )


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str, user=Depends(require_permission("communication", "read"))):
    return await CommunicationService.get_message(str(user.tenant_id), message_id)


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    data: MessageCreate,
    user=Depends(require_permission("communication", "manage")),
):
    return await CommunicationService.create_message(str(user.tenant_id), data, str(user.id))


@router.patch("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    data: MessageUpdate,
    user=Depends(require_permission("communication", "manage")),
):
    return await CommunicationService.update_message(
        str(user.tenant_id), message_id, data, str(user.id)
    )


@router.post("/messages/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: str,
    user=Depends(require_permission("communication", "read")),
):
    return await CommunicationService.mark_read(str(user.tenant_id), message_id, str(user.id))


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    user=Depends(require_permission("communication", "manage")),
):
    await CommunicationService.delete_message(str(user.tenant_id), message_id, str(user.id))
