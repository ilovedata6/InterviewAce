from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_login_uc
from app.application.dto.auth import LoginInput
from app.application.use_cases.auth import LoginUseCase
from app.core.middleware import limiter
from app.domain.exceptions import AccountLockedError, AuthenticationError
from app.schemas.auth import Token

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user",
    response_description="JWT access and refresh tokens.",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUseCase = Depends(get_login_uc),
):
    """Authenticate with email and password.

    Returns a JWT access token (15 min) and a refresh token (7 days).

    Raises:
        401: Incorrect email or password.
        403: Email not yet verified.
        429: Rate limit exceeded (5 req/min).
    """
    try:
        result = await use_case.execute(
            LoginInput(
                email=form_data.username,
                password=form_data.password,
                ip_address="127.0.0.1",
            )
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
        ) from e
    except AuthenticationError as e:
        if "verify your email" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.message,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        ) from e
    return {
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "token_type": result.token_type,
    }
