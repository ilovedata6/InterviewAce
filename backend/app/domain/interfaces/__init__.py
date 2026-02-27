"""Domain interfaces (ports) — abstract contracts for infrastructure adapters."""

from app.domain.interfaces.email_service import IEmailService
from app.domain.interfaces.file_storage import IFileStorage
from app.domain.interfaces.llm_provider import ILLMProvider
from app.domain.interfaces.repositories import (
    IInterviewRepository,
    IResumeRepository,
    IUserRepository,
)

__all__ = [
    "IUserRepository",
    "IResumeRepository",
    "IInterviewRepository",
    "ILLMProvider",
    "IFileStorage",
    "IEmailService",
]
