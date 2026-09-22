from unittest.mock import patch

from app.services.rag.retriever import build_retrieval_query, retrieve_context


def test_build_retrieval_query_combines_available_parts():
    query = build_retrieval_query("python.sql-injection", "Possible SQL injection", "python")
    assert "python.sql-injection" in query
    assert "SQL injection" in query


def test_build_retrieval_query_skips_missing_parts():
    query = build_retrieval_query(None, "XSS detected", None)
    assert query == "XSS detected"


def test_retrieve_context_returns_empty_when_store_empty():
    with patch("app.services.rag.retriever.vector_store.count", return_value=0):
        result = retrieve_context("rule", "message")
    assert result == []


def test_retrieve_context_shapes_results():
    fake_query_result = {
        "documents": [["SQL injection happens when..."]],
        "metadatas": [[{"title": "SQL Injection", "source": "sql_injection.md", "cwe": "CWE-89", "owasp": "A03", "category": "Injection"}]],
        "distances": [[0.2]],
    }
    with patch("app.services.rag.retriever.vector_store.count", return_value=4), \
         patch("app.services.rag.retriever.embed_text", return_value=[0.1, 0.2, 0.3]), \
         patch("app.services.rag.retriever.vector_store.query", return_value=fake_query_result):
        result = retrieve_context("python.sql-injection", "possible SQL injection")

    assert len(result) == 1
    assert result[0]["title"] == "SQL Injection"
    assert result[0]["cwe"] == "CWE-89"
    assert result[0]["score"] == 0.8
