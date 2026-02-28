"""
OpenAI LLM provider — primary provider implementing ILLMProvider.

Uses the OpenAI Python SDK with ``response_format={"type":"json_object"}``
for structured JSON output (no markdown fence cleaning needed).
"""

from __future__ import annotations

import json
import time
from typing import Any

import structlog
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import ILLMProvider

logger = structlog.get_logger(__name__)

# GPT-5 models can be slow — retry on timeout with exponential back-off
_TIMEOUT_RETRIES = 2
_TIMEOUT_BACKOFF_BASE = 5  # seconds


class OpenAIProvider(ILLMProvider):
    """Concrete ILLMProvider backed by the OpenAI API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5-2025-08-07",
        timeout: int = 180,
        max_retries: int = 3,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
        self._model = model
        self._client = OpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        logger.info("openai_provider_initialized", model=model, timeout=timeout)

    # ------------------------------------------------------------------
    # Retry wrapper for timeout-prone GPT-5 calls
    # ------------------------------------------------------------------

    def _call_with_timeout_retry(self, method_name: str, **create_kwargs) -> Any:
        """Call chat.completions.create with retry on APITimeoutError."""
        last_exc: Exception | None = None
        for attempt in range(1, _TIMEOUT_RETRIES + 2):  # 1-based, total = retries+1
            try:
                return self._client.chat.completions.create(**create_kwargs)
            except APITimeoutError as exc:
                last_exc = exc
                if attempt <= _TIMEOUT_RETRIES:
                    wait = _TIMEOUT_BACKOFF_BASE * attempt
                    logger.warning(
                        "openai_timeout_retry",
                        method=method_name,
                        attempt=attempt,
                        wait_seconds=wait,
                    )
                    time.sleep(wait)
                else:
                    raise
        raise last_exc  # unreachable, but keeps mypy happy

    # ------------------------------------------------------------------
    # ILLMProvider interface
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def generate_questions(self, prompts: dict[str, str]) -> list[dict[str, str] | str]:
        """
        Generate interview questions using OpenAI JSON mode.

        Expects ``prompts`` with keys ``system_prompt`` and ``user_prompt``.
        Returns a list of dicts with keys: question, type, difficulty.
        Falls back to plain strings if LLM returns unstructured items.
        """
        try:
            response = self._call_with_timeout_retry(
                "generate_questions",
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompts["system_prompt"]},
                    {"role": "user", "content": prompts["user_prompt"]},
                ],
            )
            raw = response.choices[0].message.content or ""
            data = json.loads(raw)

            # Accept both {"questions": [...]} and top-level [...]
            questions_list = data if isinstance(data, list) else data.get("questions", [])

            results: list[dict[str, str] | str] = []
            for item in questions_list:
                if isinstance(item, dict) and "question" in item:
                    results.append(item)  # preserve type/difficulty metadata
                elif isinstance(item, str):
                    results.append(item)
                else:
                    logger.warning("unexpected_question_item", item=repr(item))

            logger.info("openai_questions_generated", count=len(results), model=self._model)
            return results

        except (APIError, APITimeoutError, RateLimitError) as exc:
            logger.error("openai_api_error", method="generate_questions", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_questions failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            logger.error("openai_json_error", method="generate_questions", error=str(exc))
            raise LLMProviderError(f"OpenAI JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("openai_unexpected_error", method="generate_questions", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_questions unexpected error: {exc}") from exc

    def generate_feedback(self, prompts: dict[str, str]) -> dict[str, Any]:
        """
        Generate interview feedback/evaluation using OpenAI JSON mode.
        """
        try:
            response = self._call_with_timeout_retry(
                "generate_feedback",
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompts["system_prompt"]},
                    {"role": "user", "content": prompts["user_prompt"]},
                ],
            )
            raw = response.choices[0].message.content or ""
            result = json.loads(raw)
            logger.info("openai_feedback_generated", model=self._model)
            return result

        except (APIError, APITimeoutError, RateLimitError) as exc:
            logger.error("openai_api_error", method="generate_feedback", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_feedback failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            logger.error("openai_json_error", method="generate_feedback", error=str(exc))
            raise LLMProviderError(f"OpenAI JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("openai_unexpected_error", method="generate_feedback", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_feedback unexpected error: {exc}") from exc

    def generate_completion(self, prompt: str) -> str:
        """
        Generate a free-form text completion.
        """
        try:
            response = self._call_with_timeout_retry(
                "generate_completion",
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content or ""
            logger.info("openai_completion_generated", model=self._model)
            return text.strip()

        except (APIError, APITimeoutError, RateLimitError) as exc:
            logger.error("openai_api_error", method="generate_completion", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_completion failed: {exc}") from exc
        except Exception as exc:
            logger.error("openai_unexpected_error", method="generate_completion", error=str(exc))
            raise LLMProviderError(f"OpenAI generate_completion unexpected error: {exc}") from exc

    def parse_resume(self, text: str) -> dict[str, Any]:
        """
        Parse raw resume text into structured data using OpenAI JSON mode.
        """
        system_prompt = (
            "You are a professional resume parser. Extract structured data from the "
            "provided resume text. Return ONLY valid JSON with these fields:\n"
            "- name (string)\n"
            "- email (string)\n"
            "- phone (string)\n"
            "- summary (string)\n"
            "- inferred_role (string) — infer from content if not explicit\n"
            "- skills (array of strings)\n"
            "- education (array of objects: degree, university, start_date, end_date, cgpa, "
            "certification, institution, date)\n"
            "- experience (array of objects: job_title, company, start_date, end_date, description)\n"
            "- job_titles (array of strings)\n"
            "- years_of_experience (float)\n"
            "- confidence_score (float 0.0–1.0)\n"
            "- processing_time (float in seconds)\n\n"
            "If a field is missing, use null or empty array."
        )
        try:
            response = self._call_with_timeout_retry(
                "parse_resume",
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"RESUME TEXT:\n{text}"},
                ],
            )
            raw = response.choices[0].message.content or ""
            result = json.loads(raw)
            logger.info("openai_resume_parsed", model=self._model)
            return result

        except (APIError, APITimeoutError, RateLimitError) as exc:
            logger.error("openai_api_error", method="parse_resume", error=str(exc))
            raise LLMProviderError(f"OpenAI parse_resume failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            logger.error("openai_json_error", method="parse_resume", error=str(exc))
            raise LLMProviderError(f"OpenAI JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("openai_unexpected_error", method="parse_resume", error=str(exc))
            raise LLMProviderError(f"OpenAI parse_resume unexpected error: {exc}") from exc
