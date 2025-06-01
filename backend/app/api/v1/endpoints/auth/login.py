from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    create_tokens, 
    verify_password,
    check_login_attempts, 
    record_login_attempt, 
    create_user_session
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    check_login_attempts(str(user.id), "127.0.0.1", db)
    if not verify_password(form_data.password, str(user.hashed_password)):
        record_login_attempt(str(user.id), "127.0.0.1", False, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    record_login_attempt(str(user.id), "127.0.0.1", True, db)
    session_id = create_user_session(str(user.id), "127.0.0.1", None, db)
    access_token, refresh_token = create_tokens({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
