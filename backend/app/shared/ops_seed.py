"""Seed default operations data for new tenants."""

from beanie import PydanticObjectId

from app.reports.repository import ReportRepository


async def seed_ops_defaults(tenant_id: str, admin_user_id: str) -> None:
    existing = await ReportRepository.list_reports(tenant_id)
    if existing:
        return

    default_reports = [
        {
            "name": "Active Employees",
            "description": "All employees with active status",
            "entity_type": "employee",
            "filters": {"status": "active"},
            "columns": ["employee_code", "first_name", "last_name", "email", "department", "job_title"],
            "created_by": PydanticObjectId(admin_user_id),
            "is_shared": True,
        },
        {
            "name": "Open Projects",
            "description": "All active projects",
            "entity_type": "project",
            "filters": {"status": "active"},
            "columns": ["name", "code", "status", "priority", "start_date", "end_date"],
            "created_by": PydanticObjectId(admin_user_id),
            "is_shared": True,
        },
        {
            "name": "Tasks In Progress",
            "description": "Tasks currently in progress",
            "entity_type": "task",
            "filters": {"status": "in_progress"},
            "columns": ["title", "status", "priority", "due_date", "project_id"],
            "created_by": PydanticObjectId(admin_user_id),
            "is_shared": True,
        },
    ]

    for report_data in default_reports:
        await ReportRepository.create_report(tenant_id, report_data)
