
from beanie import PydanticObjectId

from app.audit.models import AuditLog


class AuditRepository:
    @staticmethod
    async def create(
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            tenant_id=PydanticObjectId(tenant_id),
            user_id=PydanticObjectId(user_id) if user_id else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            request_id=request_id,
        )
        await log.insert()
        return log

    @staticmethod
    async def list_logs(
        tenant_id: str,
        resource_type: str | None = None,
        user_id: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[AuditLog]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id)}
        if resource_type:
            filt["resource_type"] = resource_type
        if user_id:
            filt["user_id"] = PydanticObjectId(user_id)
        return await AuditLog.find(filt).sort("-created_at").skip(skip).limit(limit).to_list()
