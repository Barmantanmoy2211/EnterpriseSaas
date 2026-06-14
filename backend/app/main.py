from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.middleware import register_middleware
from app.shared.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.approval.models import ApprovalRequest
    from app.attendance.models import AttendanceRecord, LeaveRequest, LeaveType
    from app.audit.models import AuditLog
    from app.auth.models import RefreshToken, User
    from app.calendar.models import CalendarEvent
    from app.communication.models import CommunicationMessage
    from app.document.models import Document
    from app.employee.models import Employee
    from app.notifications.models import Notification
    from app.organization.models import OrgNode, OrgNodeType
    from app.performance.models import (
        ExitRequest,
        OnboardingPlan,
        OnboardingTemplate,
        PerformanceGoal,
        PerformanceReview,
        TrainingCourse,
        TrainingEnrollment,
    )
    from app.permissions.models import Permission, Role, RoleAssignment
    from app.project.models import Project
    from app.recruitment.models import Candidate, JobApplication, JobPosting
    from app.reports.models import ReportRun, SavedReport
    from app.search.models import SearchDocument
    from app.task.models import Task
    from app.tenant.models import Tenant, TenantSettings
    from app.workflow.models import WorkflowDefinition, WorkflowInstance

    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[
            Tenant,
            TenantSettings,
            User,
            RefreshToken,
            OrgNodeType,
            OrgNode,
            Role,
            Permission,
            RoleAssignment,
            AuditLog,
            Notification,
            WorkflowDefinition,
            WorkflowInstance,
            ApprovalRequest,
            SearchDocument,
            Employee,
            JobPosting,
            Candidate,
            JobApplication,
            AttendanceRecord,
            LeaveType,
            LeaveRequest,
            PerformanceReview,
            PerformanceGoal,
            TrainingCourse,
            TrainingEnrollment,
            OnboardingTemplate,
            OnboardingPlan,
            ExitRequest,
            Project,
            Task,
            CalendarEvent,
            Document,
            CommunicationMessage,
            SavedReport,
            ReportRun,
        ],
    )
    app.state.mongo_client = client
    yield
    client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="EnterpriseOS API",
        version="3.0.0",
        description="Metadata-driven multi-tenant enterprise platform",
        lifespan=lifespan,
    )
    register_middleware(app)
    register_exception_handlers(app)

    from app.analytics.router import router as analytics_router
    from app.approval.router import router as approval_router
    from app.attendance.router import leave_router
    from app.attendance.router import router as attendance_router
    from app.audit.router import router as audit_router
    from app.auth.router import router as auth_router
    from app.calendar.router import router as calendar_router
    from app.communication.router import router as communication_router
    from app.document.router import router as document_router
    from app.employee.router import router as employee_router
    from app.notifications.router import router as notifications_router
    from app.organization.router import router as org_router
    from app.performance.router import router as hr_router
    from app.permissions.router import router as permissions_router
    from app.project.router import router as project_router
    from app.recruitment.router import router as recruitment_router
    from app.reports.router import router as reports_router
    from app.search.router import router as search_router
    from app.task.router import router as task_router
    from app.tenant.router import router as tenant_router
    from app.workflow.router import router as workflow_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(tenant_router, prefix="/api/v1")
    app.include_router(org_router, prefix="/api/v1")
    app.include_router(permissions_router, prefix="/api/v1")
    app.include_router(audit_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")
    app.include_router(workflow_router, prefix="/api/v1")
    app.include_router(approval_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(employee_router, prefix="/api/v1")
    app.include_router(recruitment_router, prefix="/api/v1")
    app.include_router(attendance_router, prefix="/api/v1")
    app.include_router(leave_router, prefix="/api/v1")
    app.include_router(hr_router, prefix="/api/v1")
    app.include_router(project_router, prefix="/api/v1")
    app.include_router(task_router, prefix="/api/v1")
    app.include_router(calendar_router, prefix="/api/v1")
    app.include_router(document_router, prefix="/api/v1")
    app.include_router(communication_router, prefix="/api/v1")
    app.include_router(reports_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
