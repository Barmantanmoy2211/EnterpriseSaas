from datetime import UTC, datetime
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Account(TenantDocument):
    code: str
    name: str
    account_type: str
    balance: float = 0
    currency: str = "USD"
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "accounts"
        indexes = [
            [("tenant_id", 1), ("code", 1)],
            [("tenant_id", 1), ("account_type", 1)],
        ]


class JournalEntry(TenantDocument):
    account_id: PydanticObjectId
    entry_type: str
    amount: float
    description: str = ""
    reference: str = ""
    posted_by: PydanticObjectId
    posted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "journal_entries"
        indexes = [[("tenant_id", 1), ("account_id", 1)]]
