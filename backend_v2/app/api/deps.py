from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User
from app.domain.value_objects.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = await verify_token(token, db)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    
    return user


def require_role(*allowed_roles: UserRole):
    """
    FastAPI dependency factory for role-based access control.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN)),
        ):
            ...

    Multiple roles::

        @router.get("/staff")
        async def staff_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR)),
        ):
            ...
    """

    async def _role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = getattr(current_user, "role", UserRole.USER.value)
        if user_role not in {r.value for r in allowed_roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _role_checker