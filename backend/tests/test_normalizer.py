from pathlib import Path

from app.services.code_analysis.normalizer import (
    map_confidence,
    map_severity,
    normalize_bandit_results,
    normalize_semgrep_results,
)


def test_normalize_semgrep_results():
    source_root = Path("/tmp/project")
    raw = [
        {
            "check_id": "python.lang.security.sql-injection",
            "path": "/tmp/project/db.py",
            "start": {"line": 42},
            "extra": {
                "message": "Possible SQL injection",
                "severity": "ERROR",
                "metadata": {"confidence": "HIGH"},
                "lines": "cursor.execute(query)",
            },
        }
    ]
    result = normalize_semgrep_results(raw, source_root)
    assert len(result) == 1
    assert result[0]["source"] == "semgrep"
    assert result[0]["file"] == "db.py"
    assert result[0]["line"] == 42
    assert result[0]["raw_severity"] == "ERROR"


def test_normalize_bandit_results():
    source_root = Path("/tmp/project")
    raw = [
        {
            "test_id": "B608",
            "filename": "/tmp/project/db.py",
            "line_number": 10,
            "issue_text": "Possible SQL injection via string formatting",
            "issue_severity": "MEDIUM",
            "issue_confidence": "HIGH",
            "code": "query = f'SELECT * FROM users WHERE id={id}'",
        }
    ]
    result = normalize_bandit_results(raw, source_root)
    assert len(result) == 1
    assert result[0]["source"] == "bandit"
    assert result[0]["rule_id"] == "B608"
    assert result[0]["file"] == "db.py"


def test_map_severity_known_and_unknown():
    assert map_severity("ERROR") == "high"
    assert map_severity("HIGH") == "high"
    assert map_severity("WARNING") == "medium"
    assert map_severity(None) == "medium"
    assert map_severity("nonsense") == "medium"


def test_map_confidence_ranges():
    assert map_confidence("HIGH") == 0.85
    assert map_confidence("LOW") == 0.35
    assert 0.0 <= map_confidence(None) <= 1.0
