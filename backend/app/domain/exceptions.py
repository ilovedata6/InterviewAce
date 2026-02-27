"""
Domain exception hierarchy â€” framework-agnostic business errors.

All domain/application layers raise these exceptions.
The API layer (presentation) catches them and maps to HTTP status codes.
"""


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str = "A domain error occurred", code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Authentication & Authorization
# ---------------------------------------------------------------------------


class AuthenticationError(DomainError):
    """Invalid credentials or token."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(DomainError):
    """User lacks permission for the requested action."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class TokenError(DomainError):
    """JWT/refresh token specific errors."""

    def __init__(self, message: str = "Token is invalid or expired"):
        super().__init__(message=message, code="TOKEN_ERROR")


class SessionError(DomainError):
    """Session management errors (expired, deactivated, â€¦)."""

    def __init__(self, message: str = "Session error"):
        super().__init__(message=message, code="SESSION_ERROR")


class AccountLockedError(DomainError):
    """Too many failed login attempts."""

    def __init__(self, message: str = "Account temporarily locked"):
        super().__init__(message=message, code="ACCOUNT_LOCKED")


# ---------------------------------------------------------------------------
# Entity Not Found
# ---------------------------------------------------------------------------


class EntityNotFoundError(DomainError):
    """Requested entity does not exist."""

    def __init__(self, entity_name: str, entity_id: str | None = None):
        detail = (
            f"{entity_name} not found"
            if not entity_id
            else f"{entity_name} ({entity_id}) not found"
        )
        super().__init__(message=detail, code="NOT_FOUND")
        self.entity_name = entity_name
        self.entity_id = entity_id


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class ValidationError(DomainError):
    """Business-rule validation failure."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, code="VALIDATION_ERROR")


class DuplicateEntityError(DomainError):
    """Attempt to create an entity that already exists (e.g. duplicate email)."""

    def __init__(self, message: str = "Entity already exists"):
        super().__init__(message=message, code="DUPLICATE_ENTITY")


class PasswordPolicyError(ValidationError):
    """Password does not meet complexity requirements."""

    def __init__(self, message: str = "Password does not meet policy requirements"):
        super().__init__(message=message)
        self.code = "PASSWORD_POLICY_ERROR"


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------


class ResumeProcessingError(DomainError):
    """Resume parsing or analysis failed."""

    def __init__(self, message: str = "Resume processing failed"):
        super().__init__(message=message, code="RESUME_PROCESSING_ERROR")


class FileValidationError(DomainError):
    """Uploaded file fails validation (size, type, etc.)."""

    def __init__(self, message: str = "File validation failed"):
        super().__init__(message=message, code="FILE_VALIDATION_ERROR")


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------


class InterviewError(DomainError):
    """Generic interview session error."""

    def __init__(self, message: str = "Interview error"):
        super().__init__(message=message, code="INTERVIEW_ERROR")


class InterviewSessionNotFoundError(EntityNotFoundError):
    """Convenience alias for missing interview sessions."""

    def __init__(self, session_id: str | None = None):
        super().__init__(entity_name="InterviewSession", entity_id=session_id)


# ---------------------------------------------------------------------------
# LLM / External Provider
# ---------------------------------------------------------------------------


class LLMProviderError(DomainError):
    """All LLM providers failed (primary + fallback)."""

    def __init__(self, message: str = "LLM provider unavailable"):
        super().__init__(message=message, code="LLM_PROVIDER_ERROR")


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------


class EmailDeliveryError(DomainError):
    """Email sending failed."""

    def __init__(self, message: str = "Failed to send email"):
        super().__init__(message=message, code="EMAIL_DELIVERY_ERROR")
