from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    response_description="Authenticated user details.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user.

    Raises:
        401: Not authenticated.
    """
    return current_user
