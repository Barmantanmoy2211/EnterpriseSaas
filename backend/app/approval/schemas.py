from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    approver_id: str
    entity_type: str = ""
    entity_id: str = ""
    scope_node_id: str | None = None


class ApprovalAction(BaseModel):
    comments: str = ""


class ApprovalResponse(BaseModel):
    id: str
    workflow_instance_id: str | None
    step_id: str | None
    requester_id: str
    approver_id: str | None
    scope_node_id: str | None
    title: str
    description: str
    status: str
    comments: str
    entity_type: str
    entity_id: str
    created_at: str
