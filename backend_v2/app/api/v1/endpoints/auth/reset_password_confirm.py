from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import ResetPasswordConfirmIn, MessageOut
from app.services.auth_service import verify_and_reset_password

router = APIRouter()

@router.post(
    "/reset-password-confirm",
    response_model=MessageOut,
    summary="Complete password reset using token"
)
async def reset_password_confirm(
    payload: ResetPasswordConfirmIn,
    db: AsyncSession = Depends(get_db)
):
    success = await verify_and_reset_password(db, payload.token, payload.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    return MessageOut(message="Password has been reset successfully.")
