from fastapi import APIRouter, Depends, Query, status

from app.approval.schemas import ApprovalAction, ApprovalCreate, ApprovalResponse
from app.approval.service import ApprovalService
from app.core.security import get_current_user
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=list[ApprovalResponse])
async def list_pending_approvals(user=Depends(get_current_user)):
    return await ApprovalService.list_pending(str(user.tenant_id), str(user.id))


@router.get("/mine", response_model=list[ApprovalResponse])
async def list_my_approvals(user=Depends(get_current_user)):
    return await ApprovalService.list_mine(str(user.tenant_id), str(user.id))


@router.get("", response_model=list[ApprovalResponse])
async def list_all_approvals(
    status: str | None = Query(None),
    user=Depends(require_permission("approval", "read")),
):
    return await ApprovalService.list_all(str(user.tenant_id), status)


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str, user=Depends(get_current_user)):
    return await ApprovalService.get(str(user.tenant_id), approval_id)


@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_approval(data: ApprovalCreate, user=Depends(get_current_user)):
    return await ApprovalService.create_manual(str(user.tenant_id), data, str(user.id))


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_request(
    approval_id: str,
    data: ApprovalAction,
    user=Depends(require_permission("approval", "action")),
):
    return await ApprovalService.approve(str(user.tenant_id), approval_id, str(user.id), data.comments)


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_request(
    approval_id: str,
    data: ApprovalAction,
    user=Depends(require_permission("approval", "action")),
):
    return await ApprovalService.reject(str(user.tenant_id), approval_id, str(user.id), data.comments)
