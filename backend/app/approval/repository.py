from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.approval.models import ApprovalRequest


class ApprovalRepository:
    @staticmethod
    async def create(tenant_id: str, data: dict) -> ApprovalRequest:
        approval = ApprovalRequest(tenant_id=PydanticObjectId(tenant_id), **data)
        await approval.insert()
        return approval

    @staticmethod
    async def get(tenant_id: str, approval_id: str) -> ApprovalRequest | None:
        a = await ApprovalRequest.get(approval_id)
        if a and str(a.tenant_id) == tenant_id and not a.is_deleted:
            return a
        return None

    @staticmethod
    async def list_pending_for_approver(tenant_id: str, approver_id: str) -> list[ApprovalRequest]:
        return await ApprovalRequest.find(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "approver_id": PydanticObjectId(approver_id),
                "status": "pending",
                "is_deleted": False,
            }
        ).sort("-created_at").to_list()

    @staticmethod
    async def list_for_requester(tenant_id: str, requester_id: str) -> list[ApprovalRequest]:
        return await ApprovalRequest.find(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "requester_id": PydanticObjectId(requester_id),
                "is_deleted": False,
            }
        ).sort("-created_at").to_list()

    @staticmethod
    async def list_all(tenant_id: str, status: str | None = None) -> list[ApprovalRequest]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await ApprovalRequest.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def resolve(approval: ApprovalRequest, status: str, resolved_by: str, comments: str) -> ApprovalRequest:
        approval.status = status
        approval.resolved_by = PydanticObjectId(resolved_by)
        approval.resolved_at = datetime.now(UTC)
        approval.comments = comments
        await approval.touch()
        return approval
