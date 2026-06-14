from datetime import datetime
from typing import Any

from beanie import PydanticObjectId
from pydantic import EmailStr, Field

from app.shared.base_model import TenantDocument


class User(TenantDocument):
    email: EmailStr
    password_hash: str
    first_name: str = ""
    last_name: str = ""
    status: str = "active"
    profile: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "users"
        indexes = [
            [("tenant_id", 1), ("email", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]


class RefreshToken(TenantDocument):
    user_id: PydanticObjectId
    token_hash: str
    expires_at: datetime
    revoked: bool = False

    class Settings:
        name = "refresh_tokens"
        indexes = [
            [("tenant_id", 1), ("user_id", 1)],
            [("token_hash", 1)],
        ]
