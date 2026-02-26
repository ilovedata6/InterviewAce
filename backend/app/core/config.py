from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import json
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Centralized application settings.
    All values are read from environment variables or .env file.
    No insecure defaults for secrets — app will refuse to start.
    """

    # ── Project Info ──────────────────────────────────────────────────────
    PROJECT_NAME: str = "Interview Ace"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── Security (REQUIRED — no defaults) ─────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        insecure_values = {"your-secret-key-here", "", "changeme", "secret", "test"}
        if v in insecure_values:
            raise ValueError(
                "SECRET_KEY must be set to a secure random value. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Comma-separated fallback
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Database ──────────────────────────────────────────────────────────
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "interview_ace"
    DATABASE_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Construct sync DATABASE_URL (used by Alembic CLI)."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        """Construct async DATABASE_URL for asyncpg driver (used by the app)."""
        sync_url = self.database_url
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # ── File Upload ───────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    # ── Rate Limiting ─────────────────────────────────────────────────────
    RATE_LIMIT: int = 100  # requests per minute
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # ── Password Policy ───────────────────────────────────────────────────
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_SPECIAL_CHAR: bool = True
    REQUIRE_NUMBER: bool = True
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True

    # ── Session ───────────────────────────────────────────────────────────
    SESSION_TIMEOUT: int = 30  # minutes
    MAX_SESSIONS_PER_USER: int = 5

    # ── SMTP Email ────────────────────────────────────────────────────────
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_PORT: int = 587
    EMAIL_FROM: str = ""
    EMAIL_DEV_MODE: bool = True  # When True, emails are printed to console instead of sent via SMTP

    # ── Frontend URL (used for share links, email verification) ───────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Interview Defaults ────────────────────────────────────────────────
    INTERVIEW_DEFAULT_QUESTION_COUNT: int = 12
    INTERVIEW_MAX_QUESTION_COUNT: int = 30
    INTERVIEW_MIN_QUESTION_COUNT: int = 5

    # ── LLM — OpenAI (Primary) ────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.2-2025-12-11"

    # ── LLM — Gemini (Fallback) ───────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── LLM — Provider chain ──────────────────────────────────────────────
    LLM_PRIMARY_PROVIDER: str = "openai"  # "openai" | "gemini"
    LLM_TIMEOUT: int = 60  # seconds per LLM call
    LLM_MAX_RETRIES: int = 2

    # ── Legacy alias (used by existing services until migration) ──────────
    @property
    def LLM_API_KEY(self) -> Optional[str]:
        """Backward compat: returns GEMINI_API_KEY for v1 services."""
        return self.GEMINI_API_KEY or None

    # ── Redis (Celery broker, token blacklist, rate limiting) ─────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Sentry (error monitoring — leave empty to disable) ────────────────
    SENTRY_DSN: str = ""

    @property
    def is_email_configured(self) -> bool:
        """Return True if real SMTP is properly configured."""
        return bool(
            self.SMTP_SERVER
            and self.SMTP_SERVER != "smtp.example.com"
            and self.SMTP_USERNAME
            and self.SMTP_PASSWORD
        )

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

