"""
Backward-compatibility shim — delegates to the new LLM provider infrastructure.

.. deprecated::
    Use ``app.infrastructure.llm.factory.get_llm_provider()`` directly.
"""

from __future__ import annotations

import structlog
import warnings
from typing import Any, Dict, List

from app.infrastructure.llm.factory import get_llm_provider

logger = structlog.get_logger(__name__)


class LLMClient:
    """Legacy wrapper — kept for any code that still imports it."""

    def __init__(self, api_key: str | None = None):
        warnings.warn(
            "LLMClient is deprecated. Use get_llm_provider() from "
            "app.infrastructure.llm.factory instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._provider = get_llm_provider()

    def generate_questions(self, prompts: dict) -> list:
        return self._provider.generate_questions(prompts)

    def generate_feedback(self, prompts: dict) -> dict:
        return self._provider.generate_feedback(prompts)
