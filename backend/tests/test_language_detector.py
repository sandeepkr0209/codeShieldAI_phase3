from pathlib import Path

from app.services.code_analysis.language_detector import analyzers_for, detect_language


def test_detects_python():
    assert detect_language(Path("app/main.py")) == "python"


def test_detects_typescript():
    assert detect_language(Path("src/App.tsx")) == "typescript"


def test_unknown_extension_returns_none():
    assert detect_language(Path("README.md")) is None


def test_analyzers_for_python_includes_bandit():
    analyzers = analyzers_for("python")
    assert "semgrep" in analyzers
    assert "bandit" in analyzers


def test_analyzers_for_go_excludes_bandit():
    analyzers = analyzers_for("go")
    assert "bandit" not in analyzers


def test_analyzers_for_none_language():
    assert analyzers_for(None) == []
