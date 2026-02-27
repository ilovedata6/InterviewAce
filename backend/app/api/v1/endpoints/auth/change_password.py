from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_change_password_uc, get_current_user
from app.application.dto.auth import ChangePasswordInput
from app.application.use_cases.auth import ChangePasswordUseCase
from app.domain.exceptions import ValidationError
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest
from app.schemas.base import Message

router = APIRouter()


@router.post(
    "/change-password",
    response_model=Message,
    summary="Change password",
    response_description="Password change confirmation.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_uc),
):
    """Change the authenticated user's password.

    Raises:
        400: Old password incorrect or new password same as old.
        401: Not authenticated.
    """
    try:
        msg = await use_case.execute(
            current_user.id,
            ChangePasswordInput(
                old_password=payload.old_password,
                new_password=payload.new_password,
            ),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message),
        ) from e
    return {"message": msg}
