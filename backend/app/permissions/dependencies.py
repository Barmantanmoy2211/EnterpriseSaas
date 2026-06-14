from collections.abc import Callable

from fastapi import Depends

from app.core.security import get_current_user
from app.permissions.service import PermissionService
from app.shared.exceptions import ForbiddenError


def require_permission(resource: str, action: str) -> Callable:
    async def checker(user=Depends(get_current_user)):
        has_perm = await PermissionService.user_has_permission(
            str(user.tenant_id),
            str(user.id),
            resource,
            action,
        )
        if not has_perm:
            raise ForbiddenError(f"Missing permission: {resource}:{action}")
        return user

    return checker
