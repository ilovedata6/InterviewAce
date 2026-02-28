"""
LLM Provider Factory — constructs an ordered provider chain with automatic
fallback.  The primary provider is determined by ``settings.LLM_PRIMARY_PROVIDER``.

If only one API key is configured, returns a single provider (no fallback).
If neither key is configured, raises ``LLMProviderError`` at call time.

Usage::

    from app.infrastructure.llm.factory import get_llm_provider
    provider = get_llm_provider()          # single provider with fallback
    questions = provider.generate_questions(prompts)
"""

from __future__ import annotations

from typing import Any

import structlog

from app.core.config import settings
from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import ILLMProvider
from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider

logger = structlog.get_logger(__name__)


class LLMProviderWithFallback(ILLMProvider):
    """
    Composite provider that delegates to *primary* and, on failure,
    transparently retries with *fallback*.

    Implements ILLMProvider so callers are unaware of the retry logic.
    """

    def __init__(self, primary: ILLMProvider, fallback: ILLMProvider) -> None:
        self._primary = primary
        self._fallback = fallback
        logger.info(
            "llm_fallback_chain_initialized",
            primary=primary.provider_name,
            fallback=fallback.provider_name,
        )

    @property
    def provider_name(self) -> str:
        return f"{self._primary.provider_name}+{self._fallback.provider_name}"

    # ------------------------------------------------------------------
    # Delegate helpers
    # ------------------------------------------------------------------

    def _call_with_fallback(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Try *primary*; on ``LLMProviderError`` retry with *fallback*."""
        try:
            return getattr(self._primary, method_name)(*args, **kwargs)
        except LLMProviderError as exc:
            logger.warning(
                "primary_provider_failed",
                provider=self._primary.provider_name,
                method=method_name,
                error=str(exc),
                fallback=self._fallback.provider_name,
            )
            try:
                return getattr(self._fallback, method_name)(*args, **kwargs)
            except LLMProviderError:
                logger.error(
                    "fallback_provider_failed",
                    provider=self._fallback.provider_name,
                    method=method_name,
                )
                raise

    # ------------------------------------------------------------------
    # ILLMProvider interface
    # ------------------------------------------------------------------

    def generate_questions(self, prompts: dict[str, str]) -> list[dict[str, str] | str]:
        return self._call_with_fallback("generate_questions", prompts)

    def generate_feedback(self, prompts: dict[str, str]) -> dict[str, Any]:
        return self._call_with_fallback("generate_feedback", prompts)

    def generate_completion(self, prompt: str) -> str:
        return self._call_with_fallback("generate_completion", prompt)

    def parse_resume(self, text: str) -> dict[str, Any]:
        return self._call_with_fallback("parse_resume", text)


# ------------------------------------------------------------------
# Factory helper — safe provider instantiation
# ------------------------------------------------------------------


def _try_build_openai() -> OpenAIProvider | None:
    """Return an OpenAI provider if the API key is configured, else None."""
    if not settings.OPENAI_API_KEY:
        logger.info("openai_provider_skipped", reason="OPENAI_API_KEY is empty")
        return None
    return OpenAIProvider(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        timeout=settings.LLM_TIMEOUT,
        max_retries=settings.LLM_MAX_RETRIES,
    )


def _try_build_gemini() -> GeminiProvider | None:
    """Return a Gemini provider if the API key is configured, else None."""
    if not settings.GEMINI_API_KEY:
        logger.info("gemini_provider_skipped", reason="GEMINI_API_KEY is empty")
        return None
    return GeminiProvider(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )


def get_llm_provider() -> ILLMProvider:
    """
    Build the composite LLM provider based on ``settings.LLM_PRIMARY_PROVIDER``.

    Returns an ``LLMProviderWithFallback`` wrapping *primary* → *fallback*
    when both API keys are available.

    If only one API key is available, returns a single provider without fallback.
    If neither API key is configured, raises ``LLMProviderError``.
    """
    primary_name = settings.LLM_PRIMARY_PROVIDER.lower()

    # Build both providers (returns None if key is empty)
    openai = _try_build_openai()
    gemini = _try_build_gemini()

    # Determine primary / fallback based on setting
    if primary_name == "openai":
        primary, fallback = openai, gemini
    elif primary_name == "gemini":
        primary, fallback = gemini, openai
    else:
        raise LLMProviderError(
            f"Unknown LLM_PRIMARY_PROVIDER: '{settings.LLM_PRIMARY_PROVIDER}'. "
            "Expected 'openai' or 'gemini'."
        )

    # Return the best available configuration
    if primary and fallback:
        return LLMProviderWithFallback(primary=primary, fallback=fallback)
    elif primary:
        logger.warning("llm_no_fallback", provider=primary.provider_name)
        return primary
    elif fallback:
        logger.warning(
            "llm_primary_unavailable_using_fallback",
            fallback=fallback.provider_name,
        )
        return fallback
    else:
        raise LLMProviderError(
            "No LLM provider configured. Set at least one of "
            "OPENAI_API_KEY or GEMINI_API_KEY in your .env file."
        )
