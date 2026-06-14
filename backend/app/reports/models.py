from datetime import UTC, datetime
from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class SavedReport(TenantDocument):
    name: str
    description: str = ""
    entity_type: str
    filters: dict[str, Any] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list)
    created_by: PydanticObjectId
    is_shared: bool = False

    class Settings:
        name = "saved_reports"
        indexes = [[("tenant_id", 1), ("entity_type", 1)]]


class ReportRun(TenantDocument):
    report_id: PydanticObjectId
    run_by: PydanticObjectId
    row_count: int = 0
    result_preview: list[dict[str, Any]] = Field(default_factory=list)
    run_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "report_runs"
        indexes = [[("tenant_id", 1), ("report_id", 1)]]
