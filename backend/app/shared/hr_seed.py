"""Seed default HR data for new tenants."""

from app.attendance.repository import LeaveRepository
from app.performance.repository import OnboardingRepository
from app.workflow.repository import WorkflowRepository


async def seed_hr_defaults(tenant_id: str, admin_user_id: str) -> None:
    leave_types = [
        {"code": "annual", "name": "Annual Leave", "days_allowed": 20, "is_paid": True},
        {"code": "sick", "name": "Sick Leave", "days_allowed": 10, "is_paid": True},
        {"code": "unpaid", "name": "Unpaid Leave", "days_allowed": 0, "is_paid": False},
    ]
    existing_types = await LeaveRepository.list_types(tenant_id)
    existing_codes = {t.code for t in existing_types}
    for lt in leave_types:
        if lt["code"] not in existing_codes:
            await LeaveRepository.create_type(tenant_id, lt)

    existing_wf = await WorkflowRepository.get_definition_by_code(tenant_id, "leave_approval")
    if existing_wf is None:
        await WorkflowRepository.create_definition(
            tenant_id,
            {
                "code": "leave_approval",
                "name": "Leave Approval",
                "description": "Standard leave request approval workflow",
                "entity_type": "leave_request",
                "steps": [
                    {
                        "id": "manager_approval",
                        "name": "Manager Approval",
                        "type": "approval",
                        "config": {
                            "title": "Leave request pending approval",
                            "fallback_approver_id": admin_user_id,
                        },
                    },
                    {
                        "id": "notify_employee",
                        "name": "Notify Employee",
                        "type": "notification",
                        "config": {
                            "title": "Leave request processed",
                            "body": "Your leave request has been processed",
                        },
                    },
                ],
            },
        )

    templates = await OnboardingRepository.list_templates(tenant_id)
    if not templates:
        await OnboardingRepository.create_template(
            tenant_id,
            {
                "name": "Standard Employee Onboarding",
                "description": "Default onboarding checklist for new hires",
                "tasks": [
                    {"title": "Complete HR paperwork", "order": 1, "completed": False},
                    {"title": "IT equipment setup", "order": 2, "completed": False},
                    {"title": "Team introduction", "order": 3, "completed": False},
                    {"title": "Policy training", "order": 4, "completed": False},
                ],
            },
        )
