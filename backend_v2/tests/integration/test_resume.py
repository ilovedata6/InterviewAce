"""
Integration tests for resume endpoints.

Covers:
- POST /resume/upload (with mock file and mock LLM)
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
        """Upload a tiny PDF-like file with the LLM mocked."""
        # Minimal raw bytes pretending to be a PDF
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content for testing")
        fake_pdf.name = "test_resume.pdf"

        with (
            patch(
                "app.services.resume_parser.get_llm_provider",
                return_value=mock_llm_provider,
            ),
            patch(
                "app.utils.file_handler.validate_file",  # skip extension/size check
            ),
            patch(
                "app.utils.file_handler.save_upload_file",  # don't write to disk
            ),
            patch(
                "app.services.resume_parser._extract_text",
                return_value="John Doe\nSoftware Engineer\nPython, FastAPI",
            ),
            patch("os.path.getsize", return_value=2048),
        ):
            resp = await client.post(
                API + "/",
                headers=auth_headers,
                files={"file": ("test_resume.pdf", fake_pdf, "application/pdf")},
            )

        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "analyzed"
        assert "id" in data


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
