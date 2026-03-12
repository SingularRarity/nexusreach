from fastapi import Depends, HTTPException, status

from app.core.auth import current_active_user
from app.models.user import User, UserRole


def require_role(allowed_roles: list[UserRole]):  # noqa: ANN201
    """Dependency factory that restricts endpoint to specific user roles."""

    async def _check_role(
        user: User = Depends(current_active_user),  # noqa: B008
    ) -> User:
        if user.role not in allowed_roles:
            required = [r.value for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role.value}' not allowed. Required: {required}",
            )
        return user

    return _check_role
