from fastapi import APIRouter, Depends, Query

from app.audit.schemas import AuditLogListResponse, AuditLogQuery
from app.audit.service import AuditService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    resource_type: str | None = Query(None),
    user_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    user=Depends(require_permission("audit", "read")),
):
    query = AuditLogQuery(
        resource_type=resource_type,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )
    items, total = await AuditService.list_logs(str(user.tenant_id), query)
    return AuditLogListResponse(items=items, total=total)
