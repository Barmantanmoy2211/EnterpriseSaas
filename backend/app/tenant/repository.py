from beanie import PydanticObjectId

from app.tenant.models import Tenant, TenantSettings


class TenantRepository:
    @staticmethod
    async def get_by_id(tenant_id: str) -> Tenant | None:
        return await Tenant.get(tenant_id)

    @staticmethod
    async def get_by_slug(slug: str) -> Tenant | None:
        return await Tenant.find_one({"slug": slug})

    @staticmethod
    async def create(slug: str, name: str) -> Tenant:
        tenant = Tenant(slug=slug, name=name)
        await tenant.insert()
        settings = TenantSettings(tenant_id=tenant.id)
        await settings.insert()
        return tenant

    @staticmethod
    async def get_settings(tenant_id: str) -> TenantSettings | None:
        return await TenantSettings.find_one({"tenant_id": PydanticObjectId(tenant_id)})

    @staticmethod
    async def update_settings(tenant_id: str, data: dict) -> TenantSettings:
        settings = await TenantRepository.get_settings(tenant_id)
        if settings is None:
            settings = TenantSettings(tenant_id=PydanticObjectId(tenant_id))
            await settings.insert()
        for key, value in data.items():
            if value is not None:
                setattr(settings, key, value)
        from datetime import UTC, datetime

        settings.updated_at = datetime.now(UTC)
        await settings.save()
        return settings

    @staticmethod
    async def update_tenant(tenant_id: str, name: str | None = None) -> Tenant:
        tenant = await Tenant.get(tenant_id)
        if tenant is None:
            raise ValueError("Tenant not found")
        if name is not None:
            tenant.name = name
        from datetime import UTC, datetime

        tenant.updated_at = datetime.now(UTC)
        await tenant.save()
        return tenant
