from typing import Any

from pydantic import BaseModel, Field


class WorkflowStepSchema(BaseModel):
    id: str
    name: str
    type: str = Field(..., pattern="^(approval|action|notification)$")
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinitionCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    entity_type: str = Field(..., min_length=1, max_length=100)
    steps: list[WorkflowStepSchema] = Field(default_factory=list)


class WorkflowDefinitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    steps: list[WorkflowStepSchema] | None = None
    is_active: bool | None = None


class WorkflowDefinitionResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    entity_type: str
    steps: list[dict[str, Any]]
    is_active: bool


class WorkflowInstanceCreate(BaseModel):
    definition_code: str
    entity_type: str
    entity_id: str
    context: dict[str, Any] = Field(default_factory=dict)
    scope_node_id: str | None = None


class WorkflowInstanceResponse(BaseModel):
    id: str
    definition_id: str
    entity_type: str
    entity_id: str
    current_step_id: str | None
    status: str
    context: dict[str, Any]
    history: list[dict[str, Any]]
    initiated_by: str
