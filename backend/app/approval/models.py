from datetime import datetime

from beanie import PydanticObjectId

from app.shared.base_model import TenantDocument


class ApprovalRequest(TenantDocument):
    workflow_instance_id: PydanticObjectId | None = None
    step_id: str | None = None
    requester_id: PydanticObjectId
    approver_id: PydanticObjectId | None = None
    scope_node_id: PydanticObjectId | None = None
    title: str
    description: str = ""
    status: str = "pending"
    comments: str = ""
    entity_type: str = ""
    entity_id: str = ""
    resolved_at: datetime | None = None
    resolved_by: PydanticObjectId | None = None

    class Settings:
        name = "approval_requests"
        indexes = [
            [("tenant_id", 1), ("status", 1)],
            [("tenant_id", 1), ("approver_id", 1), ("status", 1)],
            [("tenant_id", 1), ("requester_id", 1)],
        ]
