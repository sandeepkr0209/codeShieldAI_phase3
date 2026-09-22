from app.services.rag.ingestion import _chunk_by_section, _parse_frontmatter, _clean_text


def test_parse_frontmatter_extracts_metadata():
    raw = """---
title: SQL Injection
cwe: CWE-89
owasp: A03:2021 - Injection
---

# SQL Injection

Some body text.
"""
    metadata, body = _parse_frontmatter(raw)
    assert metadata["title"] == "SQL Injection"
    assert metadata["cwe"] == "CWE-89"
    assert "# SQL Injection" in body


def test_parse_frontmatter_handles_missing_frontmatter():
    raw = "Just plain text, no frontmatter."
    metadata, body = _parse_frontmatter(raw)
    assert metadata == {}
    assert body == raw


def test_chunk_by_section_splits_on_headers():
    body = "# Title\n\nIntro text.\n\n## Section A\n\nContent A.\n\n## Section B\n\nContent B."
    chunks = _chunk_by_section(body, max_chars=900)
    assert len(chunks) >= 2
    assert any("Section A" in c for c in chunks)
    assert any("Section B" in c for c in chunks)


def test_clean_text_collapses_excess_blank_lines():
    text = "line1\n\n\n\n\nline2"
    assert "\n\n\n" not in _clean_text(text)
