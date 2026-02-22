from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.base import Message
from app.schemas.auth import ChangePasswordRequest

router = APIRouter()

@router.post(
    "/change-password",
    response_model=Message,
    summary="Change password",
    response_description="Password change confirmation.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated user's password.

    Raises:
        400: Old password incorrect or new password same as old.
        401: Not authenticated.
    """
    if not verify_password(payload.old_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    if payload.old_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from old password"
        )
    current_user.hashed_password = get_password_hash(payload.new_password)  # type: ignore
    db.add(current_user)
    await db.commit()
    return {"message": "Password changed successfully"}
