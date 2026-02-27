from fastapi import APIRouter, Depends, Request

from app.api.deps import get_reset_password_request_uc
from app.application.use_cases.auth import ResetPasswordRequestUseCase
from app.core.middleware import limiter
from app.schemas.auth import MessageOut, ResetPasswordRequestIn

router = APIRouter()


@router.post(
    "/reset-password-request", response_model=MessageOut, summary="Initiate forgot-password flow"
)
@limiter.limit("3/minute")
async def reset_password_request(
    request: Request,
    payload: ResetPasswordRequestIn,
    use_case: ResetPasswordRequestUseCase = Depends(get_reset_password_request_uc),
):
    msg = await use_case.execute(payload.email)
    return MessageOut(message=msg)
