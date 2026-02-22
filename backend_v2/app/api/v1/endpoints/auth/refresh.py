from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_tokens, TokenException, get_current_user_from_refresh_token
from app.db.session import get_db
from app.schemas.auth import Token

router = APIRouter()

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    refresh_token = auth_header.split(" ")[1]
    try:
        user = await get_current_user_from_refresh_token(refresh_token, db)
    except TokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    access_token, new_refresh_token = create_tokens({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
