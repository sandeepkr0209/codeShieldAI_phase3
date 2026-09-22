"""
Knowledge Base (RAG) routes — read-only stats for the frontend's
Knowledge Base page. Global reference data (not user-owned), but still
requires authentication like every other page in the app. Ingestion
itself runs via `python -m app.services.rag.ingestion` (see README).
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.knowledge import KnowledgeStats
from app.services.rag import vector_store

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/stats", response_model=KnowledgeStats)
def get_knowledge_stats(current_user: User = Depends(get_current_user)) -> KnowledgeStats:
    return KnowledgeStats(indexed_chunks=vector_store.count(), documents=vector_store.distinct_sources())
