"""
Analyzer/dependency availability check (Group 1).

Runs once at the start of a scan so the pipeline can honestly report
"completed with limited analysis" instead of silently skipping a tool.
Never assumes GPU availability — sentence-transformers/torch are
checked as CPU-capable only; CUDA is never required.
"""
import logging
import shutil

logger = logging.getLogger(__name__)


def check_analyzer_availability() -> dict[str, bool]:
    """Returns {tool_name: available} for every tool the pipeline can use."""
    availability: dict[str, bool] = {}

    availability["semgrep"] = shutil.which("semgrep") is not None
    availability["bandit"] = shutil.which("bandit") is not None

    try:
        import tree_sitter_languages  # noqa: F401

        availability["tree_sitter"] = True
    except ImportError:
        availability["tree_sitter"] = False

    try:
        import chromadb  # noqa: F401

        availability["chromadb"] = True
    except ImportError:
        availability["chromadb"] = False

    try:
        import sentence_transformers  # noqa: F401

        availability["sentence_transformers"] = True
    except ImportError:
        availability["sentence_transformers"] = False

    try:
        import playwright  # noqa: F401

        availability["playwright"] = True
    except ImportError:
        availability["playwright"] = False

    try:
        import groq  # noqa: F401
        from app.core.config import get_settings

        availability["llm"] = bool(get_settings().GROQ_API_KEY)
    except ImportError:
        availability["llm"] = False

    return availability


def build_warning_string(availability: dict[str, bool]) -> str | None:
    """Turns {"bandit": False, ...} into a short, user-facing warning
    string, or None if everything required is available."""
    unavailable = [tool for tool, ok in availability.items() if not ok]
    if not unavailable:
        return None
    labels = {
        "semgrep": "Semgrep not installed — static analysis limited to Bandit only",
        "bandit": "Bandit not installed — Python-specific checks skipped",
        "tree_sitter": "tree-sitter-languages not installed — structural parsing skipped",
        "chromadb": "ChromaDB not installed — RAG knowledge retrieval unavailable",
        "sentence_transformers": "sentence-transformers not installed — RAG embeddings unavailable",
        "playwright": "Playwright not installed (or `playwright install chromium` not run) — page/form discovery skipped, falling back to single-URL HTTPX checks only",
        "llm": "GROQ_API_KEY not configured — findings will use rule-based explanations only",
    }
    return " | ".join(labels.get(tool, f"{tool} unavailable") for tool in unavailable)
