from uuid import UUID
from typing import cast
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import ResetPasswordRequestIn, MessageOut
from app.models.user import User
from app.services.auth_service import create_password_reset_token
from app.utils.email_service import send_email

router = APIRouter()

@router.post(
    "/reset-password-request",
    response_model=MessageOut,
    summary="Initiate forgot-password flow"
)
def reset_password_request(
    payload: ResetPasswordRequestIn,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        token = create_password_reset_token(db, cast(UUID, user.id))
        reset_link = f"https://your-frontend-domain.com/reset-password?token={token}"
        email_body = (
            f"Hi {user.email},\n\n"
            "You requested a password reset. Click the link below (valid for 15 minutes):\n"
            f"{reset_link}\n\n"
            "If you did not request this, ignore this email.\n"
        )
        send_email(to_email=str(user.email), subject="Reset Your Interview Ace Password", body=email_body)
    return MessageOut(message="If an account with that email exists, you will receive a reset link shortly.")
