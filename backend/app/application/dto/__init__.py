"""Data Transfer Objects — flat structures for crossing layer boundaries."""

from app.application.dto.auth import (
    RegisterInput,
    LoginInput,
    TokenPair,
    ChangePasswordInput,
    ResetPasswordInput,
)
from app.application.dto.interview import (
    StartInterviewInput,
    SubmitAnswerInput,
    QuestionResult,
    InterviewSummaryResult,
)
from app.application.dto.resume import (
    ResumeUploadInput,
    ResumeUpdateInput,
    ResumeListInput,
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
