"""
Normalizes raw Semgrep / Bandit output into the CodeShieldAI
Observation format. Observations are raw tool signals — NOT
confirmed vulnerabilities (see app.models.observation).
"""
from pathlib import Path
from typing import Any


def normalize_semgrep_results(results: list[dict[str, Any]], source_root: Path) -> list[dict[str, Any]]:
    normalized = []
    for r in results:
        extra = r.get("extra", {})
        try:
            rel_path = str(Path(r.get("path", "")).relative_to(source_root))
        except ValueError:
            rel_path = r.get("path", "")

        start = r.get("start", {}) or {}
        end = r.get("end", {}) or {}

        normalized.append(
            {
                "source": "semgrep",
                "observation_type": "static_analysis",
                "rule_id": r.get("check_id"),
                "file": rel_path,
                "line": start.get("line"),
                "start_line": start.get("line"),
                "end_line": end.get("line"),
                "start_column": start.get("col"),
                "end_column": end.get("col"),
                "message": extra.get("message", "Semgrep finding"),
                "raw_severity": extra.get("severity", "INFO"),
                "raw_confidence": (extra.get("metadata", {}) or {}).get("confidence", "MEDIUM"),
                "code_snippet": extra.get("lines"),
            }
        )
    return normalized


def normalize_bandit_results(results: list[dict[str, Any]], source_root: Path) -> list[dict[str, Any]]:
    normalized = []
    for r in results:
        try:
            rel_path = str(Path(r.get("filename", "")).relative_to(source_root))
        except ValueError:
            rel_path = r.get("filename", "")

        # Bandit gives a `line_range` list when the issue spans multiple
        # lines; fall back to just line_number (no fabricated end line).
        line_range = r.get("line_range") or []
        end_line = line_range[-1] if len(line_range) > 1 else None

        normalized.append(
            {
                "source": "bandit",
                "observation_type": "static_analysis",
                "rule_id": r.get("test_id"),
                "file": rel_path,
                "line": r.get("line_number"),
                "start_line": r.get("line_number"),
                "end_line": end_line,
                "start_column": r.get("col_offset"),
                "end_column": None,  # Bandit doesn't report an end column
                "message": r.get("issue_text", "Bandit finding"),
                "raw_severity": r.get("issue_severity", "LOW"),
                "raw_confidence": r.get("issue_confidence", "LOW"),
                "code_snippet": r.get("code"),
            }
        )
    return normalized


_SEVERITY_MAP = {
    # Semgrep
    "ERROR": "high", "WARNING": "medium", "INFO": "low",
    # Bandit
    "HIGH": "high", "MEDIUM": "medium", "LOW": "low",
}

_CONFIDENCE_MAP = {
    "HIGH": 0.85, "MEDIUM": 0.6, "LOW": 0.35,
}


def map_severity(raw_severity: str | None) -> str:
    if not raw_severity:
        return "medium"
    return _SEVERITY_MAP.get(raw_severity.upper(), "medium")


def map_confidence(raw_confidence: str | None) -> float:
    if not raw_confidence:
        return 0.5
    return _CONFIDENCE_MAP.get(raw_confidence.upper(), 0.5)
