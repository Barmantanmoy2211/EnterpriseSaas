from beanie import PydanticObjectId

from app.audit.models import AuditLog
from app.audit.repository import AuditRepository
from app.audit.schemas import AuditLogQuery, AuditLogResponse


class AuditService:
    @staticmethod
    def _to_response(log: AuditLog) -> AuditLogResponse:
        return AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            request_id=log.request_id,
            created_at=log.created_at.isoformat(),
        )

    @staticmethod
    async def log_event(
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        return await AuditRepository.create(
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            request_id=request_id,
        )

    @staticmethod
    async def list_logs(tenant_id: str, query: AuditLogQuery) -> tuple[list[AuditLogResponse], int]:
        logs = await AuditRepository.list_logs(
            tenant_id,
            resource_type=query.resource_type,
            user_id=query.user_id,
            limit=query.limit,
            skip=query.skip,
        )
        total = await AuditLog.find({"tenant_id": PydanticObjectId(tenant_id)}).count()
        return [AuditService._to_response(log) for log in logs], total
