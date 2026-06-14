from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Role(TenantDocument):
    code: str
    name: str
    description: str = ""
    is_system: bool = False
    permission_ids: list[PydanticObjectId] = Field(default_factory=list)

    class Settings:
        name = "roles"
        indexes = [[("tenant_id", 1), ("code", 1)]]


class Permission(TenantDocument):
    resource: str
    action: str
    description: str = ""
    conditions: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "permissions"
        indexes = [[("tenant_id", 1), ("resource", 1), ("action", 1)]]


class RoleAssignment(TenantDocument):
    user_id: PydanticObjectId
    role_id: PydanticObjectId
    scope_node_id: PydanticObjectId | None = None

    class Settings:
        name = "role_assignments"
        indexes = [
            [("tenant_id", 1), ("user_id", 1)],
            [("tenant_id", 1), ("role_id", 1)],
        ]
