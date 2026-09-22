"""
LLMProvider abstraction.

The Security Agent (Phase 4) and every other consumer of LLM
capabilities should depend on this interface, never on a specific
vendor SDK directly. This lets us add or swap providers later
without rewriting business logic.
"""
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a free-form natural-language response for a prompt."""
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self, prompt: str, schema_hint: str, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """
        Generate a structured (JSON) response.

        `schema_hint` describes the expected JSON shape in plain language
        or as an example, since Phase 1 does not yet enforce a formal
        JSON schema — that lands with the Security Agent in Phase 4.
        """
        raise NotImplementedError
