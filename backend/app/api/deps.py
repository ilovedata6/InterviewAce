"""
FastAPI dependency-injection wiring.

Provides:
- ``get_current_user`` / ``require_role``  — authentication
- Repository factories (one per domain aggregate)
- Use-case factories (one per business operation)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User
from app.domain.value_objects.enums import UserRole

# ── Repository interfaces ───────────────────────────────────────────────────
from app.domain.interfaces.repositories import (
    IAuthRepository,
    IInterviewRepository,
    IResumeRepository,
    IUserRepository,
)
from app.domain.interfaces.llm_provider import ILLMProvider

# ── Concrete repositories ──────────────────────────────────────────────────
from app.infrastructure.persistence.repositories import (
    AuthRepository,
    InterviewRepository,
    ResumeRepository,
    UserRepository,
)
from app.infrastructure.llm.factory import get_llm_provider

# ── Use cases ───────────────────────────────────────────────────────────────
from app.application.use_cases.auth import (
    ChangePasswordUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
    ResendVerificationUseCase,
    ResetPasswordConfirmUseCase,
    ResetPasswordRequestUseCase,
    VerifyEmailUseCase,
)
from app.application.use_cases.interview import (
    CompleteInterviewUseCase,
    GetHistoryUseCase,
    GetNextQuestionUseCase,
    GetSessionUseCase,
    GetSummaryUseCase,
    StartInterviewUseCase,
    SubmitAnswerUseCase,
)
from app.application.use_cases.resume import (
    DeleteResumeUseCase,
    GetResumeUseCase,
    ListResumesUseCase,
    UpdateResumeUseCase,
    UploadResumeUseCase,
)

# ── Bearer token scheme ─────────────────────────────────────────────────────
bearer_scheme = HTTPBearer()


# =====================================================================
# Authentication dependencies
# =====================================================================

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = await verify_token(token, db)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    
    return user


def require_role(*allowed_roles: UserRole):
    """
    FastAPI dependency factory for role-based access control.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN)),
        ):
            ...
    """

    async def _role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = getattr(current_user, "role", UserRole.USER.value)
        if user_role not in {r.value for r in allowed_roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _role_checker


# =====================================================================
# Repository factories
# =====================================================================

async def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)


async def get_auth_repo(db: AsyncSession = Depends(get_db)) -> IAuthRepository:
    return AuthRepository(db)


async def get_resume_repo(db: AsyncSession = Depends(get_db)) -> IResumeRepository:
    return ResumeRepository(db)


async def get_interview_repo(db: AsyncSession = Depends(get_db)) -> IInterviewRepository:
    return InterviewRepository(db)


def get_llm() -> ILLMProvider:
    return get_llm_provider()


# =====================================================================
# Auth use-case factories
# =====================================================================

async def get_register_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> RegisterUseCase:
    return RegisterUseCase(user_repo)


async def get_login_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
    auth_repo: IAuthRepository = Depends(get_auth_repo),
) -> LoginUseCase:
    return LoginUseCase(user_repo, auth_repo)


async def get_logout_uc(
    auth_repo: IAuthRepository = Depends(get_auth_repo),
) -> LogoutUseCase:
    return LogoutUseCase(auth_repo)


async def get_refresh_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(user_repo)


async def get_change_password_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(user_repo)


async def get_verify_email_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> VerifyEmailUseCase:
    return VerifyEmailUseCase(user_repo)


async def get_resend_verification_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> ResendVerificationUseCase:
    return ResendVerificationUseCase(user_repo)


async def get_reset_password_request_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
    auth_repo: IAuthRepository = Depends(get_auth_repo),
) -> ResetPasswordRequestUseCase:
    return ResetPasswordRequestUseCase(user_repo, auth_repo)


async def get_reset_password_confirm_uc(
    user_repo: IUserRepository = Depends(get_user_repo),
    auth_repo: IAuthRepository = Depends(get_auth_repo),
) -> ResetPasswordConfirmUseCase:
    return ResetPasswordConfirmUseCase(user_repo, auth_repo)


# =====================================================================
# Interview use-case factories
# =====================================================================

async def get_start_interview_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
    resume_repo: IResumeRepository = Depends(get_resume_repo),
    llm: ILLMProvider = Depends(get_llm),
) -> StartInterviewUseCase:
    return StartInterviewUseCase(interview_repo, resume_repo, llm)


async def get_submit_answer_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
) -> SubmitAnswerUseCase:
    return SubmitAnswerUseCase(interview_repo)


async def get_next_question_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
) -> GetNextQuestionUseCase:
    return GetNextQuestionUseCase(interview_repo)


async def get_complete_interview_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
    llm: ILLMProvider = Depends(get_llm),
) -> CompleteInterviewUseCase:
    return CompleteInterviewUseCase(interview_repo, llm)


async def get_session_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
) -> GetSessionUseCase:
    return GetSessionUseCase(interview_repo)


async def get_history_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
) -> GetHistoryUseCase:
    return GetHistoryUseCase(interview_repo)


async def get_summary_uc(
    interview_repo: IInterviewRepository = Depends(get_interview_repo),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> GetSummaryUseCase:
    return GetSummaryUseCase(interview_repo, user_repo)


# =====================================================================
# Resume use-case factories
# =====================================================================

async def get_upload_resume_uc(
    resume_repo: IResumeRepository = Depends(get_resume_repo),
) -> UploadResumeUseCase:
    return UploadResumeUseCase(resume_repo)


async def get_list_resumes_uc(
    resume_repo: IResumeRepository = Depends(get_resume_repo),
) -> ListResumesUseCase:
    return ListResumesUseCase(resume_repo)


async def get_get_resume_uc(
    resume_repo: IResumeRepository = Depends(get_resume_repo),
) -> GetResumeUseCase:
    return GetResumeUseCase(resume_repo)


async def get_update_resume_uc(
    resume_repo: IResumeRepository = Depends(get_resume_repo),
) -> UpdateResumeUseCase:
    return UpdateResumeUseCase(resume_repo)


async def get_delete_resume_uc(
    resume_repo: IResumeRepository = Depends(get_resume_repo),
) -> DeleteResumeUseCase:
    return DeleteResumeUseCase(resume_repo)