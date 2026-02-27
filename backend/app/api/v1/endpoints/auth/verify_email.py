from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_verify_email_uc
from app.application.use_cases.auth import VerifyEmailUseCase
from app.domain.exceptions import ValidationError
from app.schemas.auth import EmailVerificationRequest, VerificationResponse

router = APIRouter()


@router.post(
    "/verify-email",
    response_model=VerificationResponse,
    summary="Verify email address",
    response_description="Verification result.",
)
async def verify_email(
    payload: EmailVerificationRequest,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_uc),
):
    """Confirm a user's email address using a one-time verification token.

    Raises:
        400: Invalid or expired verification token.
    """
    try:
        msg = await use_case.execute(payload.token)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e.message)) from e
    return VerificationResponse(message=msg)
