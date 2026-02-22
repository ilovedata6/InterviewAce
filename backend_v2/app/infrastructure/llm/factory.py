"""
LLM Provider Factory — constructs an ordered provider chain with automatic
fallback.  The primary provider is determined by ``settings.LLM_PRIMARY_PROVIDER``.

Usage::

    from app.infrastructure.llm.factory import get_llm_provider
    provider = get_llm_provider()          # single provider with fallback
    questions = provider.generate_questions(prompts)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.core.config import settings
from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import ILLMProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


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
            "LLMProviderWithFallback: primary=%s, fallback=%s",
            primary.provider_name,
            fallback.provider_name,
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
                "Primary provider (%s) failed for %s: %s — falling back to %s",
                self._primary.provider_name,
                method_name,
                exc,
                self._fallback.provider_name,
            )
            try:
                return getattr(self._fallback, method_name)(*args, **kwargs)
            except LLMProviderError:
                logger.error(
                    "Fallback provider (%s) also failed for %s",
                    self._fallback.provider_name,
                    method_name,
                )
                raise

    # ------------------------------------------------------------------
    # ILLMProvider interface
    # ------------------------------------------------------------------

    def generate_questions(self, prompts: Dict[str, str]) -> List[str]:
        return self._call_with_fallback("generate_questions", prompts)

    def generate_feedback(self, prompts: Dict[str, str]) -> Dict[str, Any]:
        return self._call_with_fallback("generate_feedback", prompts)

    def generate_completion(self, prompt: str) -> str:
        return self._call_with_fallback("generate_completion", prompt)

    def parse_resume(self, text: str) -> Dict[str, Any]:
        return self._call_with_fallback("parse_resume", text)


# ------------------------------------------------------------------
# Factory function
# ------------------------------------------------------------------

def _build_openai_provider() -> OpenAIProvider:
    return OpenAIProvider(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        timeout=settings.LLM_TIMEOUT,
        max_retries=settings.LLM_MAX_RETRIES,
    )


def _build_gemini_provider() -> GeminiProvider:
    return GeminiProvider(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )


def get_llm_provider() -> ILLMProvider:
    """
    Build the composite LLM provider based on ``settings.LLM_PRIMARY_PROVIDER``.

    Returns an ``LLMProviderWithFallback`` wrapping *primary* → *fallback*.
    If only one API key is available, returns a single provider without fallback.
    """
    primary_name = settings.LLM_PRIMARY_PROVIDER.lower()

    if primary_name == "openai":
        primary = _build_openai_provider()
        fallback = _build_gemini_provider()
    elif primary_name == "gemini":
        primary = _build_gemini_provider()
        fallback = _build_openai_provider()
    else:
        raise ValueError(
            f"Unknown LLM_PRIMARY_PROVIDER: '{settings.LLM_PRIMARY_PROVIDER}'. "
            "Expected 'openai' or 'gemini'."
        )

    return LLMProviderWithFallback(primary=primary, fallback=fallback)
