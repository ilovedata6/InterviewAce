"""Application use-cases — one class per business operation."""

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

__all__ = [
    # Auth
    "RegisterUseCase",
    "LoginUseCase",
    "LogoutUseCase",
    "RefreshTokenUseCase",
    "ChangePasswordUseCase",
    "VerifyEmailUseCase",
    "ResendVerificationUseCase",
    "ResetPasswordRequestUseCase",
    "ResetPasswordConfirmUseCase",
    # Interview
    "StartInterviewUseCase",
    "SubmitAnswerUseCase",
    "GetNextQuestionUseCase",
    "CompleteInterviewUseCase",
    "GetSessionUseCase",
    "GetHistoryUseCase",
    "GetSummaryUseCase",
    # Resume
    "UploadResumeUseCase",
    "ListResumesUseCase",
    "GetResumeUseCase",
    "UpdateResumeUseCase",
    "DeleteResumeUseCase",
]
