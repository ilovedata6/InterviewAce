from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import TokenException
from app.db.session import get_db
from app.schemas.auth import Token
from app.application.use_cases.auth import RefreshTokenUseCase
from app.api.deps import get_refresh_uc

router = APIRouter()

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    response_description="New JWT access and refresh tokens.",
)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    use_case: RefreshTokenUseCase = Depends(get_refresh_uc),
):
    """Exchange a valid refresh token for a new access/refresh pair.

    Raises:
        401: Missing, expired, or revoked refresh token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    token = auth_header.split(" ")[1]
    try:
        result = await use_case.execute(token, db)
    except TokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    return {
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "token_type": result.token_type,
    }
