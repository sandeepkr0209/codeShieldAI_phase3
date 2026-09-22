"""
Pydantic schemas for the AI integration test endpoint.

This is intentionally minimal in Phase 1 — it only validates that
the LLMProvider abstraction and Groq integration work end to end.
The Security Agent's structured reasoning schema is a Phase 4 concern.
"""
from pydantic import BaseModel, Field


class AITestRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class AITestResponse(BaseModel):
    prompt: str
    response: str
    model: str
