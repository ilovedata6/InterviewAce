from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import ResendVerificationRequest, VerificationResponse
from app.models.user import User
from app.core.security import generate_email_verification_token
from app.utils.email_utils import send_verification_email

router = APIRouter()

@router.post(
    "/resend-verification",
    response_model=VerificationResponse,
    summary="Resend verification email",
    response_description="Confirmation that a verification email was sent.",
)
async def resend_verification(
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resend the email verification link.

    Always returns success to prevent user enumeration.
    """
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()
    if not user or user.is_email_verified is True:
        # Do not reveal if user exists or is already verified
        return VerificationResponse(message="Verification email sent again.")
    token = generate_email_verification_token(str(user.id))
    send_verification_email(str(user.email), token)
    return VerificationResponse(message="Verification email sent again.")
