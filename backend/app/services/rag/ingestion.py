"""
RAG document ingestion pipeline:

  Document -> text extraction -> cleaning -> chunking -> metadata
  -> embeddings -> vector database

Source documents live as Markdown files with YAML-ish frontmatter in
services/rag/knowledge_data/. Call `ingest_knowledge_base()` once
(e.g. via the CLI entrypoint below, or automatically on first use) to
(re)populate the vector store.
"""
import logging
import re
from pathlib import Path
from typing import Any

from app.services.rag import vector_store
from app.services.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge_data"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw
    meta_block, body = match.groups()
    metadata: dict[str, str] = {}
    for line in meta_block.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _chunk_by_section(body: str, max_chars: int = 900) -> list[str]:
    """Chunks by markdown ## sections, further splitting any section
    that's still too large. Simple and explainable for a viva."""
    sections = re.split(r"(?=^## )", body, flags=re.MULTILINE)
    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            for i in range(0, len(section), max_chars):
                chunks.append(section[i : i + max_chars])
    return chunks


def ingest_knowledge_base() -> int:
    """Reads every .md file in knowledge_data/, chunks it, embeds each
    chunk, and upserts it into the vector store. Returns the number of
    chunks ingested. Safe to re-run (upsert, not append)."""
    if not KNOWLEDGE_DIR.exists():
        logger.warning("Knowledge data directory not found: %s", KNOWLEDGE_DIR)
        return 0

    all_ids: list[str] = []
    all_documents: list[str] = []
    all_metadatas: list[dict[str, Any]] = []

    for doc_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        raw = doc_path.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(raw)
        body = _clean_text(body)
        chunks = _chunk_by_section(body)

        for idx, chunk in enumerate(chunks):
            all_ids.append(f"{doc_path.stem}::{idx}")
            all_documents.append(chunk)
            all_metadatas.append(
                {
                    "source": doc_path.name,
                    "title": metadata.get("title", doc_path.stem),
                    "category": metadata.get("category", ""),
                    "cwe": metadata.get("cwe", ""),
                    "owasp": metadata.get("owasp", ""),
                    "chunk_index": idx,
                }
            )

    if not all_documents:
        return 0

    embeddings = embed_texts(all_documents)
    vector_store.upsert_chunks(ids=all_ids, embeddings=embeddings, documents=all_documents, metadatas=all_metadatas)
    logger.info("Ingested %d knowledge chunks from %s", len(all_documents), KNOWLEDGE_DIR)
    return len(all_documents)


if __name__ == "__main__":
    # Manual re-ingestion entrypoint: python -m app.services.rag.ingestion
    logging.basicConfig(level=logging.INFO)
    n = ingest_knowledge_base()
    print(f"Ingested {n} chunks.")
