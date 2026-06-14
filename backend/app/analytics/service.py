from typing import Any

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.approval.models import ApprovalRequest
from app.employee.models import Employee
from app.project.models import Project
from app.recruitment.models import JobApplication, JobPosting
from app.task.models import Task
from app.task.repository import TaskRepository


class AnalyticsOverview(BaseModel):
    employees: dict[str, int] = Field(default_factory=dict)
    projects: dict[str, int] = Field(default_factory=dict)
    tasks: dict[str, int] = Field(default_factory=dict)
    recruitment: dict[str, int] = Field(default_factory=dict)
    approvals: dict[str, int] = Field(default_factory=dict)
    totals: dict[str, int] = Field(default_factory=dict)


class AnalyticsService:
    @staticmethod
    async def _count_by_field(model: type, tenant_id: str, field: str) -> dict[str, int]:
        pipeline = [
            {"$match": {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}},
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        ]
        results = await model.aggregate(pipeline).to_list()
        return {str(r["_id"]): r["count"] for r in results if r["_id"] is not None}

    @staticmethod
    async def _total(model: type, tenant_id: str) -> int:
        return await model.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).count()

    @staticmethod
    async def get_overview(tenant_id: str) -> AnalyticsOverview:
        employees_by_status = await AnalyticsService._count_by_field(Employee, tenant_id, "status")
        projects_by_status = await AnalyticsService._count_by_field(Project, tenant_id, "status")
        tasks_by_status = await TaskRepository.count_by_status(tenant_id)
        jobs_total = await AnalyticsService._total(JobPosting, tenant_id)
        applications_total = await AnalyticsService._total(JobApplication, tenant_id)
        approvals_by_status = await AnalyticsService._count_by_field(
            ApprovalRequest, tenant_id, "status"
        )

        return AnalyticsOverview(
            employees=employees_by_status,
            projects=projects_by_status,
            tasks=tasks_by_status,
            recruitment={"jobs": jobs_total, "applications": applications_total},
            approvals=approvals_by_status,
            totals={
                "employees": sum(employees_by_status.values()),
                "projects": sum(projects_by_status.values()),
                "tasks": sum(tasks_by_status.values()),
                "pending_approvals": approvals_by_status.get("pending", 0),
            },
        )

    @staticmethod
    async def get_entity_trends(tenant_id: str, entity_type: str, days: int = 30) -> dict[str, Any]:
        model_map = {
            "employee": Employee,
            "project": Project,
            "task": Task,
        }
        model = model_map.get(entity_type)
        if model is None:
            return {"entity_type": entity_type, "daily_counts": []}

        from datetime import UTC, datetime, timedelta

        start = datetime.now(UTC) - timedelta(days=days)
        pipeline = [
            {
                "$match": {
                    "tenant_id": PydanticObjectId(tenant_id),
                    "is_deleted": False,
                    "created_at": {"$gte": start},
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        results = await model.aggregate(pipeline).to_list()
        return {
            "entity_type": entity_type,
            "daily_counts": [{"date": r["_id"], "count": r["count"]} for r in results],
        }
