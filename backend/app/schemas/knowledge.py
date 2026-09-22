"""
Pydantic schemas for Knowledge Base stats (RAG).
"""
from pydantic import BaseModel


class KnowledgeStats(BaseModel):
    indexed_chunks: int
    documents: list[str]


class RAGSource(BaseModel):
    title: str | None
    source: str | None
    cwe: str | None
    owasp: str | None
    score: float | None
