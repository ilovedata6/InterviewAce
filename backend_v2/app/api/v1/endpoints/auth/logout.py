from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_user,
    revoke_tokens,
    deactivate_session,
    TokenException
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.base import Message

router = APIRouter()

@router.post(
    "/logout",
    response_model=Message,
    summary="Log out current user",
    response_description="Logout confirmation.",
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke the current access/refresh token pair and deactivate the session.

    Raises:
        401: Missing or invalid authorization header.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        token = auth_header.split(" ")[1]
        try:
            await revoke_tokens(token, str(current_user.id), db)
        except TokenException as e:
            print(f"Warning: Token revocation failed: {str(e)}")
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            await deactivate_session(session_id, db)
        return {"message": "Successfully logged out"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )
