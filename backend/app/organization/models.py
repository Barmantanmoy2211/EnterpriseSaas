from typing import Any

from beanie import PydanticObjectId
from pydantic import ConfigDict, Field

from app.shared.base_model import TenantDocument


class OrgNodeType(TenantDocument):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    label: str
    allowed_child_types: list[str] = Field(default_factory=list)
    type_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")
    is_root_allowed: bool = False

    class Settings:
        name = "org_node_types"
        indexes = [[("tenant_id", 1), ("code", 1)]]


class OrgNode(TenantDocument):
    parent_id: PydanticObjectId | None = None
    node_type: str
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    path: list[str] = Field(default_factory=list)
    depth: int = 0
    sort_order: int = 0

    class Settings:
        name = "org_nodes"
        indexes = [
            [("tenant_id", 1), ("parent_id", 1)],
            [("tenant_id", 1), ("path", 1)],
            [("tenant_id", 1), ("node_type", 1)],
        ]
