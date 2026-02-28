"""
Gemini LLM provider — fallback provider implementing ILLMProvider.

Wraps the ``google-genai`` SDK.  Gemini does not expose a native JSON mode
so responses are cleaned of markdown fences before parsing.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import structlog
from google import genai

from app.domain.exceptions import LLMProviderError
from app.domain.interfaces.llm_provider import ILLMProvider

logger = structlog.get_logger(__name__)

# Retry settings for Gemini 429 rate-limit errors
_RATE_LIMIT_RETRIES = 2
_RATE_LIMIT_BACKOFF_BASE = 15  # seconds


def _clean_gemini_json(raw: str) -> str:
    """Strip markdown code-fences that Gemini sometimes wraps around JSON."""
    return re.sub(r"```(?:json)?|```", "", raw).strip()


class GeminiProvider(ILLMProvider):
    """Concrete ILLMProvider backed by Google Gemini."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider")
        self._model = model
        self._client = genai.Client(api_key=api_key)
        logger.info("gemini_provider_initialized", model=model)

    # ------------------------------------------------------------------
    # Retry wrapper for rate-limited requests
    # ------------------------------------------------------------------

    def _call_with_rate_limit_retry(self, method_name: str, **generate_kwargs) -> Any:
        """Call generate_content with retry on 429 RESOURCE_EXHAUSTED."""
        last_exc: Exception | None = None
        for attempt in range(1, _RATE_LIMIT_RETRIES + 2):
            try:
                return self._client.models.generate_content(**generate_kwargs)
            except Exception as exc:
                exc_str = str(exc)
                is_rate_limit = "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str
                if is_rate_limit and attempt <= _RATE_LIMIT_RETRIES:
                    wait = _RATE_LIMIT_BACKOFF_BASE * attempt
                    logger.warning(
                        "gemini_rate_limit_retry",
                        method=method_name,
                        attempt=attempt,
                        wait_seconds=wait,
                    )
                    time.sleep(wait)
                    last_exc = exc
                else:
                    raise
        raise last_exc  # type: ignore[misc]

    # ------------------------------------------------------------------
    # ILLMProvider interface
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def generate_questions(self, prompts: dict[str, str]) -> list[dict[str, str] | str]:
        """
        Generate interview questions using Gemini.

        Expects ``prompts`` with keys ``system_prompt`` and ``user_prompt``.
        Returns a list of dicts with keys: question, type, difficulty.
        Falls back to plain strings if LLM returns unstructured items.
        """
        try:
            full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
            response = self._call_with_rate_limit_retry(
                "generate_questions",
                model=self._model,
                contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            )
            raw = (response.text or "").strip()
            if not raw:
                raise ValueError("Gemini response is empty")

            cleaned = _clean_gemini_json(raw)
            data = json.loads(cleaned)

            questions_list = data if isinstance(data, list) else data.get("questions", [])

            results: list[dict[str, str] | str] = []
            for item in questions_list:
                if isinstance(item, dict) and "question" in item:
                    results.append(item)  # preserve type/difficulty metadata
                elif isinstance(item, str):
                    results.append(item)
                else:
                    logger.warning("unexpected_question_item", item=repr(item))

            logger.info("gemini_questions_generated", count=len(results), model=self._model)
            return results

        except json.JSONDecodeError as exc:
            logger.error("gemini_json_error", method="generate_questions", error=str(exc))
            raise LLMProviderError(f"Gemini JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("gemini_error", method="generate_questions", error=str(exc))
            raise LLMProviderError(f"Gemini generate_questions failed: {exc}") from exc

    def generate_feedback(self, prompts: dict[str, str]) -> dict[str, Any]:
        """Generate interview feedback/evaluation."""
        try:
            full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
            response = self._call_with_rate_limit_retry(
                "generate_feedback",
                model=self._model,
                contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            )
            raw = (response.text or "").strip()
            if not raw:
                raise ValueError("Gemini response is empty")

            cleaned = _clean_gemini_json(raw)
            result = json.loads(cleaned)
            logger.info("gemini_feedback_generated", model=self._model)
            return result

        except json.JSONDecodeError as exc:
            logger.error("gemini_json_error", method="generate_feedback", error=str(exc))
            raise LLMProviderError(f"Gemini JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("gemini_error", method="generate_feedback", error=str(exc))
            raise LLMProviderError(f"Gemini generate_feedback failed: {exc}") from exc

    def generate_completion(self, prompt: str) -> str:
        """Generate a free-form text completion."""
        try:
            response = self._call_with_rate_limit_retry(
                "generate_completion",
                model=self._model,
                contents=[prompt],
            )
            text = (response.text or "").strip()
            logger.info("gemini_completion_generated", model=self._model)
            return text

        except Exception as exc:
            logger.error("gemini_error", method="generate_completion", error=str(exc))
            raise LLMProviderError(f"Gemini generate_completion failed: {exc}") from exc

    def parse_resume(self, text: str) -> dict[str, Any]:
        """Parse raw resume text into structured data."""
        prompt = (
            "You are a professional resume parser. Extract structured resume data "
            "from the provided raw text.\n"
            "Return ONLY valid JSON with exactly the following fields:\n"
            "- name (string)\n"
            "- email (string)\n"
            "- phone (string)\n"
            "- summary (string)\n"
            "- inferred_role (string) – if not explicitly stated, infer from summary\n"
            "- skills (array of strings)\n"
            "- education (array of objects: degree, university, start_date, end_date, "
            "cgpa, certification, institution, date)\n"
            "- experience (array of objects: job_title, company, start_date, end_date, "
            "description)\n"
            "- job_titles (array of strings)\n"
            "- years_of_experience (float)\n"
            "- confidence_score (float 0.0–1.0)\n"
            "- processing_time (float in seconds)\n\n"
            "INSTRUCTIONS:\n"
            "• If a field is missing, use null or an empty array ([]).\n"
            "• Do not include any explanations, markdown, or extra formatting.\n"
            "• Return ONLY valid parsable JSON.\n"
            "• Use your best judgment to summarize and infer fields if not explicitly written.\n\n"
            f"TEXT:\n{text}"
        )

        try:
            response = self._call_with_rate_limit_retry(
                "parse_resume",
                model=self._model,
                contents=[prompt],
            )
            raw = (response.text or "").strip()
            cleaned = _clean_gemini_json(raw)
            result = json.loads(cleaned)
            logger.info("gemini_resume_parsed", model=self._model)
            return result

        except json.JSONDecodeError as exc:
            logger.error("gemini_json_error", method="parse_resume", error=str(exc))
            raise LLMProviderError(f"Gemini JSON decode error: {exc}") from exc
        except Exception as exc:
            logger.error("gemini_error", method="parse_resume", error=str(exc))
            raise LLMProviderError(f"Gemini parse_resume failed: {exc}") from exc
