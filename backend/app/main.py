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
    from app.audit.models import AuditLog
    from app.auth.models import RefreshToken, User
    from app.notifications.models import Notification
    from app.organization.models import OrgNode, OrgNodeType
    from app.permissions.models import Permission, Role, RoleAssignment
    from app.search.models import SearchDocument
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
        ],
    )
    app.state.mongo_client = client
    yield
    client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="EnterpriseOS API",
        version="1.1.0",
        description="Metadata-driven multi-tenant enterprise platform",
        lifespan=lifespan,
    )
    register_middleware(app)
    register_exception_handlers(app)

    from app.approval.router import router as approval_router
    from app.audit.router import router as audit_router
    from app.auth.router import router as auth_router
    from app.notifications.router import router as notifications_router
    from app.organization.router import router as org_router
    from app.permissions.router import router as permissions_router
    from app.search.router import router as search_router
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

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
