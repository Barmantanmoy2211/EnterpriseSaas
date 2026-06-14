from typing import Any

from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    id: str
    resource: str
    action: str
    description: str
    conditions: dict[str, Any]


class RoleCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    permission_ids: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    permission_ids: list[str] | None = None


class RoleResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    is_system: bool
    permission_ids: list[str]


class RoleAssignmentCreate(BaseModel):
    user_id: str
    role_id: str
    scope_node_id: str | None = None


class RoleAssignmentResponse(BaseModel):
    id: str
    user_id: str
    role_id: str
    scope_node_id: str | None
