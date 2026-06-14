from app.shared.exceptions import NotFoundError
from app.tenant.repository import TenantRepository
from app.tenant.schemas import TenantSettingsUpdateRequest, TenantUpdateRequest


class TenantService:
    @staticmethod
    async def get_tenant(tenant_id: str):
        tenant = await TenantRepository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        return tenant

    @staticmethod
    async def update_tenant(tenant_id: str, data: TenantUpdateRequest):
        return await TenantRepository.update_tenant(tenant_id, name=data.name)

    @staticmethod
    async def get_settings(tenant_id: str):
        settings = await TenantRepository.get_settings(tenant_id)
        if settings is None:
            raise NotFoundError("Tenant settings not found")
        return settings

    @staticmethod
    async def update_settings(tenant_id: str, data: TenantSettingsUpdateRequest):
        update_data = data.model_dump(exclude_unset=True)
        return await TenantRepository.update_settings(tenant_id, update_data)
