"""
RAG retrieval: given an observation, build a security-focused query,
retrieve the top relevant knowledge chunks, and return them with
source metadata attached for the LLM (and for display in the UI).
"""
from typing import Any

from app.services.rag import vector_store
from app.services.rag.embeddings import embed_text


def build_retrieval_query(rule_id: str | None, message: str, language: str | None) -> str:
    parts = [p for p in [rule_id, message, language] if p]
    return " ".join(parts)


def retrieve_context(rule_id: str | None, message: str, language: str | None = None, top_k: int = 3) -> list[dict[str, Any]]:
    """Returns a list of {text, title, source, cwe, owasp, category, score}."""
    if vector_store.count() == 0:
        return []

    query_text = build_retrieval_query(rule_id, message, language)
    query_embedding = embed_text(query_text)
    result = vector_store.query(query_embedding, top_k=top_k)

    chunks: list[dict[str, Any]] = []
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": doc,
                "title": meta.get("title"),
                "source": meta.get("source"),
                "cwe": meta.get("cwe"),
                "owasp": meta.get("owasp"),
                "category": meta.get("category"),
                "score": round(1 - dist, 4) if dist is not None else None,
            }
        )
    return chunks
