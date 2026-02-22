"""
Integration tests for resume endpoints.

Covers:
- POST /resume/upload (with mock file and Celery task mocked)
- Error cases (no file, unauthenticated)
"""

from __future__ import annotations

import io
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient


API = "/api/v1/resume/upload"


class TestResumeUpload:
    async def test_upload_unauthenticated(self, client: AsyncClient):
        resp = await client.post(API + "/")
        assert resp.status_code in (401, 403, 422)

    async def test_upload_no_file(self, client: AsyncClient, auth_headers):
        resp = await client.post(API + "/", headers=auth_headers)
        assert resp.status_code == 422  # FastAPI validation — file required

    async def test_upload_success_mock_llm(
        self, client: AsyncClient, auth_headers, mock_llm_provider
    ):
        """Upload a tiny PDF-like file — Celery task is mocked, returns 202."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content for testing")
        fake_pdf.name = "test_resume.pdf"

        # Mock the Celery task .delay() to avoid needing a real broker
        mock_task_result = MagicMock()
        mock_task_result.id = "test-celery-task-id-123"

        with (
            patch(
                "app.api.v1.endpoints.resume.upload.parse_resume_task"
            ) as mock_task,
            patch(
                "app.api.v1.endpoints.resume.upload.validate_file",  # skip extension/size check
            ),
            patch(
                "app.api.v1.endpoints.resume.upload.save_upload_file",  # don't write to disk
            ),
            patch("app.api.v1.endpoints.resume.upload.os.path.getsize", return_value=2048),
        ):
            mock_task.delay.return_value = mock_task_result

            resp = await client.post(
                API + "/",
                headers=auth_headers,
                files={"file": ("test_resume.pdf", fake_pdf, "application/pdf")},
            )

        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "pending"
        assert "id" in data
        assert data["task_id"] == "test-celery-task-id-123"


class TestResumeUploadValidation:
    async def test_upload_invalid_extension(
        self, client: AsyncClient, auth_headers
    ):
        """Uploading a .txt file should fail validation."""
        fake_txt = io.BytesIO(b"plain text resume")
        resp = await client.post(
            API + "/",
            headers=auth_headers,
            files={"file": ("resume.txt", fake_txt, "text/plain")},
        )
        # validate_file should reject; exact status depends on implementation
        assert resp.status_code in (400, 422)
