from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import EmailVerificationRequest, VerificationResponse
from app.core.security import verify_email_verification_token
from app.models.user import User

router = APIRouter()

@router.post("/verify-email", response_model=VerificationResponse)
def verify_email(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    try:
        user_id = verify_email_verification_token(payload.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    if user.is_email_verified is True:
        return VerificationResponse(message="Email already verified.")
    setattr(user, 'is_email_verified', True)
    db.add(user)
    db.commit()
    return VerificationResponse(message="Email verified successfully. You can now log in.")
