from fastapi import APIRouter, Depends
from app.schemas.auth import ResendVerificationRequest, VerificationResponse
from app.application.use_cases.auth import ResendVerificationUseCase
from app.api.deps import get_resend_verification_uc

router = APIRouter()

@router.post(
    "/resend-verification",
    response_model=VerificationResponse,
    summary="Resend verification email",
    response_description="Confirmation that a verification email was sent.",
)
async def resend_verification(
    payload: ResendVerificationRequest,
    use_case: ResendVerificationUseCase = Depends(get_resend_verification_uc),
):
    """Resend the email verification link.

    Always returns success to prevent user enumeration.
    """
    msg = await use_case.execute(payload.email)
    return VerificationResponse(message=msg)
