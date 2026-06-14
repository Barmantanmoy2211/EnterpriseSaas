from datetime import UTC, datetime, timedelta

from jose import JWTError

from app.auth.repository import AuthRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.tenant_context import set_tenant_context
from app.permissions.service import PermissionService
from app.shared.exceptions import ConflictError, UnauthorizedError
from app.tenant.repository import TenantRepository


class AuthService:
    @staticmethod
    async def register(data: RegisterRequest) -> tuple[TokenResponse, UserResponse]:
        existing = await TenantRepository.get_by_slug(data.tenant_slug)
        if existing:
            raise ConflictError("Tenant slug already exists")

        existing_user = await AuthRepository.get_user_by_email_global(data.email)
        if existing_user:
            raise ConflictError("Email already registered")

        tenant = await TenantRepository.create(slug=data.tenant_slug, name=data.tenant_name)
        tenant_id = str(tenant.id)
        set_tenant_context(tenant_id, data.tenant_slug)

        user = await AuthRepository.create_user(
            tenant_id=tenant_id,
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )

        await PermissionService.seed_tenant_defaults(tenant_id, str(user.id))

        tokens = await AuthService._issue_tokens(str(user.id), tenant_id)
        return tokens, AuthService._user_response(user)

    @staticmethod
    async def login(data: LoginRequest) -> tuple[TokenResponse, UserResponse]:
        tenant = None
        if data.tenant_slug:
            tenant = await TenantRepository.get_by_slug(data.tenant_slug)
            if tenant is None:
                raise UnauthorizedError("Invalid credentials")
            user = await AuthRepository.get_user_by_email(str(tenant.id), data.email)
        else:
            user = await AuthRepository.get_user_by_email_global(data.email)
            if user:
                tenant = await TenantRepository.get_by_id(str(user.tenant_id))

        if user is None or tenant is None or tenant.status != "active":
            raise UnauthorizedError("Invalid credentials")

        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        set_tenant_context(str(tenant.id), tenant.slug)
        tokens = await AuthService._issue_tokens(str(user.id), str(tenant.id))
        from app.audit.service import AuditService

        await AuditService.log_event(
            str(tenant.id), "auth.login", "user", str(user.id), str(user.id)
        )
        return tokens, AuthService._user_response(user)

    @staticmethod
    async def refresh(refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid refresh token")
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            if not user_id or not tenant_id:
                raise UnauthorizedError("Invalid refresh token")
        except JWTError as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        record = await AuthRepository.get_refresh_token(tenant_id, refresh_token)
        if record is None or record.expires_at < datetime.now(UTC):
            raise UnauthorizedError("Refresh token expired or revoked")

        await AuthRepository.revoke_refresh_token(record)
        return await AuthService._issue_tokens(user_id, tenant_id)

    @staticmethod
    async def logout(user_id: str, tenant_id: str) -> None:
        await AuthRepository.revoke_all_user_tokens(tenant_id, user_id)

    @staticmethod
    async def _issue_tokens(user_id: str, tenant_id: str) -> TokenResponse:
        access = create_access_token(user_id, tenant_id)
        refresh = create_refresh_token(user_id, tenant_id)
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        await AuthRepository.store_refresh_token(tenant_id, user_id, refresh, expires_at)
        return TokenResponse(access_token=access, refresh_token=refresh)

    @staticmethod
    def _user_response(user) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            tenant_id=str(user.tenant_id),
        )
