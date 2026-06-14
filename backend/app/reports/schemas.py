from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SavedReportCreate(BaseModel):
    name: str
    description: str = ""
    entity_type: str
    filters: dict[str, Any] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list)
    is_shared: bool = False


class SavedReportUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    filters: dict[str, Any] | None = None
    columns: list[str] | None = None
    is_shared: bool | None = None


class SavedReportResponse(BaseModel):
    id: str
    name: str
    description: str
    entity_type: str
    filters: dict[str, Any]
    columns: list[str]
    created_by: str
    is_shared: bool


class ReportRunResponse(BaseModel):
    id: str
    report_id: str
    run_by: str
    row_count: int
    result_preview: list[dict[str, Any]]
    run_at: datetime
