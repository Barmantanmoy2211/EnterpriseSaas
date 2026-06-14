from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OrgNodeTypeCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., min_length=1, max_length=50)
    label: str = Field(..., min_length=1, max_length=200)
    allowed_child_types: list[str] = Field(default_factory=list)
    type_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")
    is_root_allowed: bool = False


class OrgNodeTypeUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    label: str | None = Field(None, min_length=1, max_length=200)
    allowed_child_types: list[str] | None = None
    type_schema: dict[str, Any] | None = Field(None, alias="schema")
    is_root_allowed: bool | None = None


class OrgNodeTypeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    code: str
    label: str
    allowed_child_types: list[str]
    type_schema: dict[str, Any] = Field(alias="schema")
    is_root_allowed: bool


class OrgNodeCreate(BaseModel):
    parent_id: str | None = None
    node_type: str
    name: str = Field(..., min_length=1, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)
    sort_order: int = 0


class OrgNodeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    metadata: dict[str, Any] | None = None
    sort_order: int | None = None


class OrgNodeMove(BaseModel):
    parent_id: str | None = None


class OrgNodeResponse(BaseModel):
    id: str
    parent_id: str | None
    node_type: str
    name: str
    metadata: dict[str, Any]
    path: list[str]
    depth: int
    sort_order: int
    children: list["OrgNodeResponse"] = Field(default_factory=list)


OrgNodeResponse.model_rebuild()
