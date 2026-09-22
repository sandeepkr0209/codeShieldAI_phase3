"""
Language detection by file extension.

Deliberately simple (extension-based) rather than content-sniffing —
sufficient for a 7th-semester project and easy to explain in a viva.
Also tracks which deterministic analyzers are actually available per
language, so the system never silently claims coverage it doesn't have.
"""
from pathlib import Path

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".php": "php",
}

# Which analyzers genuinely run for which language in this codebase.
# Semgrep's "auto" ruleset covers most of these; Bandit is Python-only.
ANALYZER_SUPPORT: dict[str, list[str]] = {
    "python": ["semgrep", "bandit"],
    "javascript": ["semgrep"],
    "typescript": ["semgrep"],
    "java": ["semgrep"],
    "c": ["semgrep"],
    "cpp": ["semgrep"],
    "csharp": ["semgrep"],
    "go": ["semgrep"],
    "php": ["semgrep"],
}

# Languages Tree-sitter structural extraction supports in this codebase.
TREE_SITTER_SUPPORT = {"python", "javascript", "typescript", "java", "go"}


def detect_language(file_path: Path) -> str | None:
    return EXTENSION_LANGUAGE_MAP.get(file_path.suffix.lower())


def analyzers_for(language: str | None) -> list[str]:
    if language is None:
        return []
    return ANALYZER_SUPPORT.get(language, [])
