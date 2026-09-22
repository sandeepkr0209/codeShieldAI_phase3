"""
LLM service package.

Use `get_llm_provider()` to obtain the configured provider instance
rather than instantiating GroqProvider directly, so callers stay
decoupled from the concrete implementation.
"""
from functools import lru_cache

from app.services.llm.groq_provider import GroqProvider
from app.services.llm.provider import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    return GroqProvider()
