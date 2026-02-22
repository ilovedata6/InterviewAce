"""
Shared pytest fixtures for the InterviewAce test suite.

* In-memory async SQLite database (via aiosqlite)
* HTTPX AsyncClient wired to the FastAPI app
* Authenticated user / token helpers
* Mock LLM provider returning deterministic responses
"""

from __future__ import annotations

import os
import uuid
from datetime import timedelta
from typing import Any, AsyncGenerator, Dict, Generator, List

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# ---------------------------------------------------------------------------
# Ensure env vars are set BEFORE importing app modules that read settings
# ---------------------------------------------------------------------------
os.environ.setdefault("SECRET_KEY", "a" * 64)
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")

# ---------------------------------------------------------------------------
# Monkey-patch SQLAlchemy UUID type for SQLite compatibility.
#
# The ORM models use ``UUID(as_uuid=True)`` which expects all bind values
# to be ``uuid.UUID`` objects (it calls ``value.hex``).  Several security
# functions pass *string* UUIDs which works with PostgreSQL's native UUID
# type but fails on SQLite.  This patch converts strings to UUID before
# the original processor runs.
# ---------------------------------------------------------------------------
import sqlalchemy.types as _sa_types

_original_uuid_bind_processor = _sa_types.Uuid.bind_processor


def _patched_uuid_bind_processor(self, dialect):
    proc = _original_uuid_bind_processor(self, dialect)
    if proc is None:
        return None

    def _safe_proc(value):
        if isinstance(value, str):
            try:
                value = uuid.UUID(value)
            except ValueError:
                pass
        return proc(value)

    return _safe_proc


_sa_types.Uuid.bind_processor = _patched_uuid_bind_processor

from app.infrastructure.persistence.models.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.core.security import get_password_hash, create_token  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.resume import Resume  # noqa: E402
from app.models.interview import InterviewSession, InterviewQuestion  # noqa: E402
from app.models.security import (  # noqa: E402, F401
    LoginAttempt, TokenBlacklist, UserSession, PasswordHistory, PasswordResetToken,
)
from app.domain.interfaces.llm_provider import ILLMProvider  # noqa: E402

# ---------------------------------------------------------------------------
# In-memory SQLite async engine (tests only)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Mock LLM Provider
# ---------------------------------------------------------------------------
class MockLLMProvider(ILLMProvider):
    """Deterministic LLM provider for use in tests — no network calls."""

    @property
    def provider_name(self) -> str:
        return "MockLLM"

    def generate_questions(self, prompts: Dict[str, str]) -> List[str]:
        return [
            "Tell me about yourself.",
            "Describe a challenging project.",
            "What are your strengths?",
        ]

    def generate_feedback(self, prompts: Dict[str, str]) -> Dict[str, Any]:
        return {
            "summary": "Good overall performance.",
            "confidence_score": 0.85,
            "questions_feedback": [],
        }

    def generate_completion(self, prompt: str) -> str:
        return "This is a mock completion response."

    def parse_resume(self, text: str) -> Dict[str, Any]:
        return {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "summary": "Experienced software engineer.",
            "inferred_role": "Software Engineer",
            "skills": ["Python", "FastAPI", "SQL"],
            "education": [
                {
                    "degree": "BSc Computer Science",
                    "university": "Test University",
                    "start_date": "2016",
                    "end_date": "2020",
                }
            ],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company": "Test Corp",
                    "start_date": "2020",
                    "end_date": "2024",
                    "description": "Built web applications.",
                }
            ],
            "job_titles": ["Software Engineer"],
            "years_of_experience": 4.0,
            "confidence_score": 0.92,
            "processing_time": 1.5,
        }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean async database session for each test."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTPX AsyncClient backed by the real FastAPI app with the DB
    dependency overridden to use the test database.
    """
    from main import app  # local import to avoid circular at collection time

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Insert and return a verified, active test user."""
    user = User(
        id=uuid.uuid4(),
        full_name="Test User",
        email="testuser@example.com",
        hashed_password=get_password_hash("Test@1234"),
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Return a valid access token for the test user."""
    return create_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Convenience: Authorization header dict for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    """Return a deterministic mock LLM provider."""
    return MockLLMProvider()
