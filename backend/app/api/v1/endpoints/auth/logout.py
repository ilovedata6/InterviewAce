from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_logout_uc
from app.application.use_cases.auth import LogoutUseCase
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
    use_case: LogoutUseCase = Depends(get_logout_uc),
):
    """Revoke the current access/refresh token pair and deactivate the session.

    Raises:
        401: Missing or invalid authorization header.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header"
        )
    token = auth_header.split(" ")[1]
    session_id = request.headers.get("X-Session-ID")
    msg = await use_case.execute(token, current_user.id, session_id, db)
    return {"message": msg}
