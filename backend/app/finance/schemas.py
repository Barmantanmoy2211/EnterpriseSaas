from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    code: str
    name: str
    account_type: str
    balance: float = 0
    currency: str = "USD"
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccountUpdate(BaseModel):
    name: str | None = None
    account_type: str | None = None
    balance: float | None = None
    currency: str | None = None
    is_active: bool | None = None
    metadata: dict[str, Any] | None = None


class AccountResponse(BaseModel):
    id: str
    code: str
    name: str
    account_type: str
    balance: float
    currency: str
    is_active: bool
    metadata: dict[str, Any]


class JournalEntryCreate(BaseModel):
    account_id: str
    entry_type: str
    amount: float
    description: str = ""
    reference: str = ""


class JournalEntryResponse(BaseModel):
    id: str
    account_id: str
    entry_type: str
    amount: float
    description: str
    reference: str
    posted_by: str
    posted_at: datetime
