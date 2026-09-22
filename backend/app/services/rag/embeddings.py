"""
Local embedding model wrapper.

Uses sentence-transformers so RAG can run entirely locally without
sending the knowledge base or code snippets to an external API. Kept
behind a thin function interface so the embedding backend is
replaceable later without touching ingestion/retrieval code.
"""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _get_model():
    from sentence_transformers import SentenceTransformer  # type: ignore

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
