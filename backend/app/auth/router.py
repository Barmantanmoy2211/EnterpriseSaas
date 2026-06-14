from fastapi import APIRouter, Depends

from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.core.security import get_current_user
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(data: RegisterRequest):
    tokens, user = await AuthService.register(data)
    return {"tokens": tokens.model_dump(), "user": user.model_dump()}


@router.post("/login", response_model=dict)
async def login(data: LoginRequest):
    tokens, user = await AuthService.login(data)
    return {"tokens": tokens.model_dump(), "user": user.model_dump()}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    return await AuthService.refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(user=Depends(get_current_user)):
    await AuthService.logout(str(user.id), str(user.tenant_id))


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return await AuthService.build_user_response(user)


@router.get("/users", response_model=list[UserResponse])
async def list_tenant_users(user=Depends(require_permission("user", "read"))):
    users = await AuthService.list_tenant_users(str(user.tenant_id))
    results = []
    for u in users:
        results.append(await AuthService.build_user_response(u))
    return results
