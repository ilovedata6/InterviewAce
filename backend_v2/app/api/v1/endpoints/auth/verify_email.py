from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import EmailVerificationRequest, VerificationResponse
from app.core.security import verify_email_verification_token
from app.models.user import User

router = APIRouter()

@router.post("/verify-email", response_model=VerificationResponse)
async def verify_email(
    payload: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_id = verify_email_verification_token(payload.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    if user.is_email_verified is True:
        return VerificationResponse(message="Email already verified.")
    setattr(user, 'is_email_verified', True)
    db.add(user)
    await db.commit()
    return VerificationResponse(message="Email verified successfully. You can now log in.")
