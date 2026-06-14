from beanie import PydanticObjectId

from app.reports.models import ReportRun, SavedReport


class ReportRepository:
    @staticmethod
    async def list_reports(tenant_id: str, entity_type: str | None = None) -> list[SavedReport]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if entity_type:
            filt["entity_type"] = entity_type
        return await SavedReport.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_report(tenant_id: str, report_id: str) -> SavedReport | None:
        report = await SavedReport.get(report_id)
        if report and str(report.tenant_id) == tenant_id and not report.is_deleted:
            return report
        return None

    @staticmethod
    async def create_report(tenant_id: str, data: dict) -> SavedReport:
        report = SavedReport(tenant_id=PydanticObjectId(tenant_id), **data)
        await report.insert()
        return report

    @staticmethod
    async def update(report: SavedReport, data: dict) -> SavedReport:
        for key, value in data.items():
            if value is not None:
                setattr(report, key, value)
        await report.touch()
        return report

    @staticmethod
    async def soft_delete(report: SavedReport) -> None:
        await report.soft_delete()

    @staticmethod
    async def create_run(tenant_id: str, data: dict) -> ReportRun:
        run = ReportRun(tenant_id=PydanticObjectId(tenant_id), **data)
        await run.insert()
        return run

    @staticmethod
    async def list_runs(tenant_id: str, report_id: str) -> list[ReportRun]:
        return await ReportRun.find(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "report_id": PydanticObjectId(report_id),
                "is_deleted": False,
            }
        ).sort("-run_at").to_list()
