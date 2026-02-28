"""
LLM Provider interface — abstract contract for language model integrations.

Concrete implementations: OpenAIProvider, GeminiProvider (Phase 3).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ILLMProvider(ABC):
    """Port for LLM interactions (question generation, feedback, parsing)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. 'OpenAI', 'Gemini')."""
        ...

    @abstractmethod
    def generate_questions(self, prompts: dict[str, str]) -> list[dict[str, str] | str]:
        """
        Generate interview questions from the given prompts.

        Args:
            prompts: Dict with keys ``system_prompt`` and ``user_prompt``.

        Returns:
            List of question dicts (with keys: question, type, difficulty)
            or plain strings as fallback.
        """
        ...

    @abstractmethod
    def generate_feedback(self, prompts: dict[str, str]) -> dict[str, Any]:
        """
        Generate evaluation feedback from the given prompts.

        Args:
            prompts: Dict with keys ``system_prompt`` and ``user_prompt``.

        Returns:
            Structured feedback as a dictionary.
        """
        ...

    @abstractmethod
    def generate_completion(self, prompt: str) -> str:
        """
        Generate a free-form text completion.

        Args:
            prompt: The input prompt string.

        Returns:
            Generated text response.
        """
        ...

    @abstractmethod
    def parse_resume(self, text: str) -> dict[str, Any]:
        """
        Parse raw resume text into structured data.

        Args:
            text: The extracted text from a resume file.

        Returns:
            Structured resume data (skills, experience, education, etc.).
        """
        ...
