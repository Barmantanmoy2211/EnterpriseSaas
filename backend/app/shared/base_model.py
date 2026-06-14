from datetime import UTC, datetime
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import Field


class TimestampMixin:
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SoftDeleteMixin:
    is_deleted: bool = False
    deleted_at: datetime | None = None


class TenantDocument(Document, TimestampMixin, SoftDeleteMixin):
    tenant_id: PydanticObjectId

    class Settings:
        is_root = False

    async def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
        await self.save()

    async def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        await self.save()


class BaseRepository:
    model: type[TenantDocument]

    @classmethod
    def _tenant_filter(cls, tenant_id: str, **extra: Any) -> dict[str, Any]:
        filt: dict[str, Any] = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        filt.update(extra)
        return filt
