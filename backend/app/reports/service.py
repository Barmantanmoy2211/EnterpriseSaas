from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.employee.models import Employee
from app.project.models import Project
from app.reports.models import SavedReport
from app.reports.repository import ReportRepository
from app.reports.schemas import (
    ReportRunResponse,
    SavedReportCreate,
    SavedReportResponse,
    SavedReportUpdate,
)
from app.shared.exceptions import NotFoundError
from app.task.models import Task

ENTITY_MODELS = {
    "employee": Employee,
    "project": Project,
    "task": Task,
}


class ReportService:
    @staticmethod
    def _report_response(report: SavedReport) -> SavedReportResponse:
        return SavedReportResponse(
            id=str(report.id),
            name=report.name,
            description=report.description,
            entity_type=report.entity_type,
            filters=report.filters,
            columns=report.columns,
            created_by=str(report.created_by),
            is_shared=report.is_shared,
        )

    @staticmethod
    async def list_reports(tenant_id: str, entity_type: str | None = None) -> list[SavedReportResponse]:
        reports = await ReportRepository.list_reports(tenant_id, entity_type)
        return [ReportService._report_response(r) for r in reports]

    @staticmethod
    async def get_report(tenant_id: str, report_id: str) -> SavedReportResponse:
        report = await ReportRepository.get_report(tenant_id, report_id)
        if report is None:
            raise NotFoundError("Report not found")
        return ReportService._report_response(report)

    @staticmethod
    async def create_report(tenant_id: str, data: SavedReportCreate, actor_id: str) -> SavedReportResponse:
        payload = data.model_dump()
        payload["created_by"] = PydanticObjectId(actor_id)
        report = await ReportRepository.create_report(tenant_id, payload)
        await AuditService.log_event(tenant_id, "report.created", "saved_report", str(report.id), actor_id)
        return ReportService._report_response(report)

    @staticmethod
    async def update_report(
        tenant_id: str, report_id: str, data: SavedReportUpdate, actor_id: str
    ) -> SavedReportResponse:
        report = await ReportRepository.get_report(tenant_id, report_id)
        if report is None:
            raise NotFoundError("Report not found")
        report = await ReportRepository.update(report, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "report.updated", "saved_report", str(report.id), actor_id)
        return ReportService._report_response(report)

    @staticmethod
    async def delete_report(tenant_id: str, report_id: str, actor_id: str) -> None:
        report = await ReportRepository.get_report(tenant_id, report_id)
        if report is None:
            raise NotFoundError("Report not found")
        await ReportRepository.soft_delete(report)
        await AuditService.log_event(tenant_id, "report.deleted", "saved_report", str(report.id), actor_id)

    @staticmethod
    async def _query_entity(tenant_id: str, entity_type: str, filters: dict) -> list[dict]:
        model = ENTITY_MODELS.get(entity_type)
        if model is None:
            return []

        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        filt.update(filters)
        docs = await model.find(filt).limit(100).to_list()
        return [d.model_dump(mode="json") for d in docs]

    @staticmethod
    async def run_report(tenant_id: str, report_id: str, actor_id: str) -> ReportRunResponse:
        report = await ReportRepository.get_report(tenant_id, report_id)
        if report is None:
            raise NotFoundError("Report not found")

        rows = await ReportService._query_entity(tenant_id, report.entity_type, report.filters)
        if report.columns:
            rows = [{k: r.get(k) for k in report.columns if k in r} for r in rows]

        preview = rows[:20]
        run = await ReportRepository.create_run(
            tenant_id,
            {
                "report_id": report.id,
                "run_by": PydanticObjectId(actor_id),
                "row_count": len(rows),
                "result_preview": preview,
            },
        )
        await AuditService.log_event(tenant_id, "report.run", "saved_report", str(report.id), actor_id)

        return ReportRunResponse(
            id=str(run.id),
            report_id=str(run.report_id),
            run_by=str(run.run_by),
            row_count=run.row_count,
            result_preview=run.result_preview,
            run_at=run.run_at,
        )

    @staticmethod
    async def list_runs(tenant_id: str, report_id: str) -> list[ReportRunResponse]:
        runs = await ReportRepository.list_runs(tenant_id, report_id)
        return [
            ReportRunResponse(
                id=str(r.id),
                report_id=str(r.report_id),
                run_by=str(r.run_by),
                row_count=r.row_count,
                result_preview=r.result_preview,
                run_at=r.run_at,
            )
            for r in runs
        ]
