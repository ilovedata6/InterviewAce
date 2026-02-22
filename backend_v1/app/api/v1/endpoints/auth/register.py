from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, generate_email_verification_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, VerificationResponse
from app.utils.email_utils import send_verification_email

router = APIRouter()

@router.post("/register", response_model=VerificationResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Generate verification token and send email
    token = generate_email_verification_token(str(db_user.id))
    send_verification_email(str(db_user.email), token)
    return VerificationResponse(message="Registration successful. Please check your email to verify your account.")
