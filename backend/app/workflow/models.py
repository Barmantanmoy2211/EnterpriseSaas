from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class WorkflowDefinition(TenantDocument):
    code: str
    name: str
    description: str = ""
    entity_type: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True

    class Settings:
        name = "workflow_definitions"
        indexes = [[("tenant_id", 1), ("code", 1)]]


class WorkflowInstance(TenantDocument):
    definition_id: PydanticObjectId
    entity_type: str
    entity_id: str
    current_step_id: str | None = None
    status: str = "pending"
    context: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] = Field(default_factory=list)
    initiated_by: PydanticObjectId

    class Settings:
        name = "workflow_instances"
        indexes = [
            [("tenant_id", 1), ("status", 1)],
            [("tenant_id", 1), ("entity_type", 1), ("entity_id", 1)],
        ]
