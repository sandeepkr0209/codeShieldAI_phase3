"""
AI integration test endpoint.

This ONLY validates that the LLMProvider -> GroqProvider path works
end to end. It is not the Security Agent — see services/security_agent/.
Requires authentication like every other page in the app.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.ai import AITestRequest, AITestResponse
from app.services.llm import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/test", response_model=AITestResponse)
def test_ai(payload: AITestRequest, current_user: User = Depends(get_current_user)) -> AITestResponse:
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY is not configured on the server. Set it in backend/.env",
        )

    provider = get_llm_provider()
    try:
        response_text = provider.generate(payload.prompt)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Groq LLM call failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider call failed: {exc}",
        ) from exc

    return AITestResponse(prompt=payload.prompt, response=response_text, model=settings.GROQ_MODEL)
