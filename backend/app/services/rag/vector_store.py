"""
ChromaDB-backed vector store, encapsulated behind a small service
interface so the underlying vector database could be swapped (e.g.
for FAISS) without touching ingestion/retrieval callers.
"""
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "chroma"
COLLECTION_NAME = "security_knowledge"


@lru_cache
def _get_client():
    import chromadb  # type: ignore

    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))


def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def upsert_chunks(ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict[str, Any]]) -> None:
    collection = _get_collection()
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(embedding: list[float], top_k: int = 4) -> dict[str, Any]:
    collection = _get_collection()
    return collection.query(query_embeddings=[embedding], n_results=top_k)


def count() -> int:
    try:
        return _get_collection().count()
    except Exception:  # noqa: BLE001
        return 0


def distinct_sources() -> list[str]:
    try:
        collection = _get_collection()
        data = collection.get(include=["metadatas"])
        titles = {m.get("title") for m in data.get("metadatas", []) if m.get("title")}
        return sorted(titles)
    except Exception:  # noqa: BLE001
        return []
