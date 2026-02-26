"""
Unit tests for the LLM provider factory and fallback chain.

Tests use mock providers to verify:
- Primary succeeds → no fallback called
- Primary fails → fallback succeeds
- Both fail → LLMProviderError raised
- Factory function returns correct provider types
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

os.environ.setdefault("SECRET_KEY", "a" * 64)
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")

from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import ILLMProvider
from app.infrastructure.llm.factory import LLMProviderWithFallback, get_llm_provider


# ---------------------------------------------------------------------------
# Helpers — lightweight mock providers
# ---------------------------------------------------------------------------

class _SuccessProvider(ILLMProvider):
    @property
    def provider_name(self) -> str:
        return "SuccessProvider"

    def generate_questions(self, prompts: Dict[str, str]) -> List[str]:
        return ["Q1", "Q2"]

    def generate_feedback(self, prompts: Dict[str, str]) -> Dict[str, Any]:
        return {"summary": "ok"}

    def generate_completion(self, prompt: str) -> str:
        return "completion"

    def parse_resume(self, text: str) -> Dict[str, Any]:
        return {"name": "Test"}


class _FailProvider(ILLMProvider):
    @property
    def provider_name(self) -> str:
        return "FailProvider"

    def _fail(self) -> None:
        raise LLMProviderError("boom")

    def generate_questions(self, prompts: Dict[str, str]) -> List[str]:
        self._fail()
        return []  # unreachable

    def generate_feedback(self, prompts: Dict[str, str]) -> Dict[str, Any]:
        self._fail()
        return {}

    def generate_completion(self, prompt: str) -> str:
        self._fail()
        return ""

    def parse_resume(self, text: str) -> Dict[str, Any]:
        self._fail()
        return {}


# ---------------------------------------------------------------------------
# Fallback chain tests
# ---------------------------------------------------------------------------

class TestLLMProviderWithFallback:
    def test_primary_success_no_fallback(self):
        primary = _SuccessProvider()
        fallback = _FailProvider()
        composite = LLMProviderWithFallback(primary, fallback)

        result = composite.generate_questions({"system_prompt": "", "user_prompt": ""})
        assert result == ["Q1", "Q2"]

    def test_primary_fails_fallback_succeeds(self):
        primary = _FailProvider()
        fallback = _SuccessProvider()
        composite = LLMProviderWithFallback(primary, fallback)

        result = composite.generate_questions({"system_prompt": "", "user_prompt": ""})
        assert result == ["Q1", "Q2"]

    def test_both_fail_raises(self):
        primary = _FailProvider()
        fallback = _FailProvider()
        composite = LLMProviderWithFallback(primary, fallback)

        with pytest.raises(LLMProviderError):
            composite.generate_questions({"system_prompt": "", "user_prompt": ""})

    def test_provider_name_combined(self):
        composite = LLMProviderWithFallback(_SuccessProvider(), _FailProvider())
        assert composite.provider_name == "SuccessProvider+FailProvider"

    def test_generate_feedback_fallback(self):
        composite = LLMProviderWithFallback(_FailProvider(), _SuccessProvider())
        result = composite.generate_feedback({"system_prompt": "", "user_prompt": ""})
        assert result == {"summary": "ok"}

    def test_generate_completion_fallback(self):
        composite = LLMProviderWithFallback(_FailProvider(), _SuccessProvider())
        result = composite.generate_completion("prompt")
        assert result == "completion"

    def test_parse_resume_fallback(self):
        composite = LLMProviderWithFallback(_FailProvider(), _SuccessProvider())
        result = composite.parse_resume("resume text")
        assert result == {"name": "Test"}


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------

class TestGetLLMProvider:
    def test_returns_fallback_composite(self):
        """With both API keys set, factory should return a composite."""
        provider = get_llm_provider()
        assert isinstance(provider, LLMProviderWithFallback)

    def test_invalid_primary_raises(self):
        with patch("app.infrastructure.llm.factory.settings") as mock_settings:
            mock_settings.LLM_PRIMARY_PROVIDER = "unknown"
            mock_settings.OPENAI_API_KEY = "key"
            mock_settings.GEMINI_API_KEY = "key"
            with pytest.raises(LLMProviderError, match="Unknown LLM_PRIMARY_PROVIDER"):
                get_llm_provider()
