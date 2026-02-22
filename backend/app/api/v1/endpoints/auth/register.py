from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.middleware import limiter
from app.schemas.auth import UserCreate, VerificationResponse
from app.application.use_cases.auth import RegisterUseCase
from app.application.dto.auth import RegisterInput
from app.api.deps import get_register_uc
from app.domain.exceptions import DuplicateEntityError

router = APIRouter()

@router.post(
    "/register",
    response_model=VerificationResponse,
    summary="Register a new account",
    response_description="Confirmation with email verification instructions.",
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    user: UserCreate,
    use_case: RegisterUseCase = Depends(get_register_uc),
):
    """Create a new user account and send a verification email.

    Raises:
        400: Email already registered.
        429: Rate limit exceeded (10 req/min).
    """
    try:
        message = await use_case.execute(
            RegisterInput(
                email=user.email,
                password=user.password,
                full_name=user.full_name,
            )
        )
    except DuplicateEntityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return VerificationResponse(message=message)
