from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.reports.schemas import ReportRunResponse, SavedReportCreate, SavedReportResponse, SavedReportUpdate
from app.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[SavedReportResponse])
async def list_reports(
    entity_type: str | None = Query(None),
    user=Depends(require_permission("report", "read")),
):
    return await ReportService.list_reports(str(user.tenant_id), entity_type)


@router.get("/{report_id}", response_model=SavedReportResponse)
async def get_report(report_id: str, user=Depends(require_permission("report", "read"))):
    return await ReportService.get_report(str(user.tenant_id), report_id)


@router.post("", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: SavedReportCreate,
    user=Depends(require_permission("report", "manage")),
):
    return await ReportService.create_report(str(user.tenant_id), data, str(user.id))


@router.patch("/{report_id}", response_model=SavedReportResponse)
async def update_report(
    report_id: str,
    data: SavedReportUpdate,
    user=Depends(require_permission("report", "manage")),
):
    return await ReportService.update_report(str(user.tenant_id), report_id, data, str(user.id))


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    user=Depends(require_permission("report", "manage")),
):
    await ReportService.delete_report(str(user.tenant_id), report_id, str(user.id))


@router.post("/{report_id}/run", response_model=ReportRunResponse)
async def run_report(report_id: str, user=Depends(require_permission("report", "read"))):
    return await ReportService.run_report(str(user.tenant_id), report_id, str(user.id))


@router.get("/{report_id}/runs", response_model=list[ReportRunResponse])
async def list_report_runs(report_id: str, user=Depends(require_permission("report", "read"))):
    return await ReportService.list_runs(str(user.tenant_id), report_id)
