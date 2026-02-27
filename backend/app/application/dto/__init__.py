"""Data Transfer Objects — flat structures for crossing layer boundaries."""

from app.application.dto.auth import (
    ChangePasswordInput,
    LoginInput,
    RegisterInput,
    ResetPasswordInput,
    TokenPair,
)
from app.application.dto.interview import (
    InterviewSummaryResult,
    QuestionResult,
    StartInterviewInput,
    SubmitAnswerInput,
)
from app.application.dto.resume import (
    ResumeListInput,
    ResumeUpdateInput,
    ResumeUploadInput,
)

__all__ = [
    "RegisterInput",
    "LoginInput",
    "TokenPair",
    "ChangePasswordInput",
    "ResetPasswordInput",
    "StartInterviewInput",
    "SubmitAnswerInput",
    "QuestionResult",
    "InterviewSummaryResult",
    "ResumeUploadInput",
    "ResumeUpdateInput",
    "ResumeListInput",
]
