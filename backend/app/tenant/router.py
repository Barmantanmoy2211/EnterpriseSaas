from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.tenant.schemas import (
    TenantResponse,
    TenantSettingsResponse,
    TenantSettingsUpdateRequest,
    TenantUpdateRequest,
)
from app.tenant.service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(user=Depends(get_current_user)):
    tenant = await TenantService.get_tenant(str(user.tenant_id))
    return TenantResponse(
        id=str(tenant.id),
        slug=tenant.slug,
        name=tenant.name,
        status=tenant.status,
        plan=tenant.plan,
    )


@router.patch("/me", response_model=TenantResponse)
async def update_my_tenant(data: TenantUpdateRequest, user=Depends(get_current_user)):
    tenant = await TenantService.update_tenant(str(user.tenant_id), data)
    return TenantResponse(
        id=str(tenant.id),
        slug=tenant.slug,
        name=tenant.name,
        status=tenant.status,
        plan=tenant.plan,
    )


@router.get("/me/settings", response_model=TenantSettingsResponse)
async def get_tenant_settings(user=Depends(get_current_user)):
    settings = await TenantService.get_settings(str(user.tenant_id))
    return TenantSettingsResponse(
        branding=settings.branding,
        auth_policy=settings.auth_policy,
        org_defaults=settings.org_defaults,
    )


@router.patch("/me/settings", response_model=TenantSettingsResponse)
async def update_tenant_settings(data: TenantSettingsUpdateRequest, user=Depends(get_current_user)):
    settings = await TenantService.update_settings(str(user.tenant_id), data)
    return TenantSettingsResponse(
        branding=settings.branding,
        auth_policy=settings.auth_policy,
        org_defaults=settings.org_defaults,
    )
