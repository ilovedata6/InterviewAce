from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_reset_password_confirm_uc
from app.application.dto.auth import ResetPasswordInput
from app.application.use_cases.auth import ResetPasswordConfirmUseCase
from app.domain.exceptions import ValidationError
from app.schemas.auth import MessageOut, ResetPasswordConfirmIn

router = APIRouter()


@router.post(
    "/reset-password-confirm",
    response_model=MessageOut,
    summary="Complete password reset using token",
)
async def reset_password_confirm(
    payload: ResetPasswordConfirmIn,
    use_case: ResetPasswordConfirmUseCase = Depends(get_reset_password_confirm_uc),
):
    try:
        msg = await use_case.execute(
            ResetPasswordInput(token=payload.token, new_password=payload.new_password)
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message)) from e
    return MessageOut(message=msg)
