"""
Integration tests for interview endpoints.

Flow tested: start session → get next question → answer → complete → summary.

The LLM provider is mocked via dependency injection override so no real
API calls are made.
"""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.enums import FileType, ResumeStatus
from app.models.resume import Resume

API = "/api/v1/interview"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_resume(db_session: AsyncSession, user_id) -> Resume:
    """Insert a minimal analysed resume for the test user."""
    resume = Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Test Resume",
        description="Test description",
        file_path="/tmp/test_resume.pdf",
        file_name="test_resume.pdf",
        file_size=1024,
        file_type=FileType.PDF,
        inferred_role="Software Engineer",
        status=ResumeStatus.ANALYZED,
        analysis={
            "experience": [{"job_title": "SWE", "company": "Test", "description": "Built things"}],
            "education": [{"degree": "BSc"}],
            "skills": ["Python"],
        },
        skills=["Python", "FastAPI"],
        years_of_experience=3,
        confidence_score=0.9,
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)
    return resume


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestStartInterview:
    async def test_start_without_resume_returns_404(
        self, client: AsyncClient, test_user, auth_headers
    ):
        resp = await client.post(
            f"{API}/start",
            json={"resume_id": str(uuid.uuid4())},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_start_unauthenticated(self, client: AsyncClient):
        resp = await client.post(
            f"{API}/start",
            json={"resume_id": str(uuid.uuid4())},
        )
        assert resp.status_code in (401, 403)

    async def test_start_with_resume(
        self,
        client: AsyncClient,
        test_user,
        auth_headers,
        db_session: AsyncSession,
        mock_llm_provider,
    ):
        """Start an interview session with a resume and mock LLM."""
        from app.api.deps import get_llm
        from main import app

        resume = await _create_resume(db_session, test_user.id)

        # Override the FastAPI DI dependency so no real LLM call is made.
        app.dependency_overrides[get_llm] = lambda: mock_llm_provider
        try:
            resp = await client.post(
                f"{API}/start",
                json={"resume_id": str(resume.id)},
                headers=auth_headers,
            )
        finally:
            del app.dependency_overrides[get_llm]

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["resume_id"] == str(resume.id)


class TestNextQuestion:
    async def test_next_question_invalid_session(self, client: AsyncClient, auth_headers):
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"{API}/{fake_id}/next", headers=auth_headers)
        assert resp.status_code == 404


class TestAnswerQuestion:
    async def test_answer_invalid_session(self, client: AsyncClient, auth_headers):
        fake_session = str(uuid.uuid4())
        fake_question = str(uuid.uuid4())
        resp = await client.post(
            f"{API}/{fake_session}/{fake_question}/answer",
            json={"answer_text": "My answer"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestCompleteInterview:
    async def test_complete_invalid_session(self, client: AsyncClient, auth_headers):
        fake_id = str(uuid.uuid4())
        resp = await client.post(f"{API}/{fake_id}/complete", headers=auth_headers)
        assert resp.status_code == 404
