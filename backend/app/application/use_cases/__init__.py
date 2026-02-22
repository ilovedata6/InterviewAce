"""Application use-cases — one class per business operation."""

from app.application.use_cases.auth import (
    RegisterUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    ChangePasswordUseCase,
    VerifyEmailUseCase,
    ResendVerificationUseCase,
    ResetPasswordRequestUseCase,
    ResetPasswordConfirmUseCase,
)
from app.application.use_cases.interview import (
    StartInterviewUseCase,
    SubmitAnswerUseCase,
    GetNextQuestionUseCase,
    CompleteInterviewUseCase,
    GetSessionUseCase,
    GetHistoryUseCase,
    GetSummaryUseCase,
)
from app.application.use_cases.resume import (
    UploadResumeUseCase,
    ListResumesUseCase,
    GetResumeUseCase,
    UpdateResumeUseCase,
    DeleteResumeUseCase,
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
