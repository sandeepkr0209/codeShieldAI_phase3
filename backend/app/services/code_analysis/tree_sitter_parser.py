"""
Tree-sitter based structural extraction.

Produces a normalized CodeStructure for a single file:
{
  "file": "...",
  "language": "...",
  "functions": [...],
  "classes": [...],
  "imports": [...],
}

Used for understanding/extraction only — this is NOT a full compiler
or type-checker. Errors during parsing are caught per-file so one bad
file never aborts the whole scan.
"""
import logging
from pathlib import Path
from typing import Any

from app.services.code_analysis.language_detector import TREE_SITTER_SUPPORT

logger = logging.getLogger(__name__)

# Node type names that represent a function/method definition, per language.
_FUNCTION_NODE_TYPES: dict[str, set[str]] = {
    "python": {"function_definition"},
    "javascript": {"function_declaration", "method_definition", "arrow_function"},
    "typescript": {"function_declaration", "method_definition", "arrow_function"},
    "java": {"method_declaration", "constructor_declaration"},
    "go": {"function_declaration", "method_declaration"},
}

_CLASS_NODE_TYPES: dict[str, set[str]] = {
    "python": {"class_definition"},
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration", "interface_declaration"},
    "java": {"class_declaration", "interface_declaration"},
    "go": {"type_declaration"},
}

_IMPORT_NODE_TYPES: dict[str, set[str]] = {
    "python": {"import_statement", "import_from_statement"},
    "javascript": {"import_statement"},
    "typescript": {"import_statement"},
    "java": {"import_declaration"},
    "go": {"import_declaration", "import_spec"},
}


def _get_parser(language: str):
    """Lazily imports tree_sitter_languages so environments without it
    installed can still run everything else (parsing is best-effort)."""
    from tree_sitter_languages import get_parser  # type: ignore

    return get_parser(language)


def _node_text(source: bytes, node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _find_name(node, source: bytes) -> str | None:
    name_node = node.child_by_field_name("name")
    if name_node is not None:
        return _node_text(source, name_node)
    return None


def extract_structure(file_path: Path, language: str | None) -> dict[str, Any]:
    structure: dict[str, Any] = {
        "file": str(file_path),
        "language": language,
        "functions": [],
        "classes": [],
        "imports": [],
    }

    if language not in TREE_SITTER_SUPPORT:
        return structure  # not supported for structural extraction — honestly reported as empty

    try:
        source = file_path.read_bytes()
        parser = _get_parser(language)
        tree = parser.parse(source)
    except Exception as exc:  # noqa: BLE001 — a single unparsable file must not abort the scan
        logger.warning("Tree-sitter failed to parse %s: %s", file_path, exc)
        return structure

    function_types = _FUNCTION_NODE_TYPES.get(language, set())
    class_types = _CLASS_NODE_TYPES.get(language, set())
    import_types = _IMPORT_NODE_TYPES.get(language, set())

    def walk(node):
        if node.type in function_types:
            structure["functions"].append(
                {"name": _find_name(node, source) or "<anonymous>", "line": node.start_point[0] + 1}
            )
        elif node.type in class_types:
            structure["classes"].append(
                {"name": _find_name(node, source) or "<anonymous>", "line": node.start_point[0] + 1}
            )
        elif node.type in import_types:
            structure["imports"].append(
                {"text": _node_text(source, node).strip().splitlines()[0][:200], "line": node.start_point[0] + 1}
            )
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return structure
