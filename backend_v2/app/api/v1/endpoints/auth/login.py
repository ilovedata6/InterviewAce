from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_tokens, 
    verify_password,
    check_login_attempts, 
    record_login_attempt, 
    create_user_session
)
from app.core.middleware import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if user.is_email_verified is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    await check_login_attempts(str(user.id), "127.0.0.1", db)
    if not verify_password(form_data.password, str(user.hashed_password)):
        await record_login_attempt(str(user.id), "127.0.0.1", False, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    await record_login_attempt(str(user.id), "127.0.0.1", True, db)
    session_id = await create_user_session(str(user.id), "127.0.0.1", None, db)
    access_token, refresh_token = create_tokens({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
