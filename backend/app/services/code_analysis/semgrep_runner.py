"""
Controlled Semgrep execution.

Runs Semgrep as a subprocess with predefined arguments only — the LLM
and the API layer never construct or influence the command line. No
shell=True, a hard timeout, and a restricted working directory.
"""
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SEMGREP_TIMEOUT_SECONDS = 180


def run_semgrep(source_root: Path) -> list[dict[str, Any]]:
    """
    Runs `semgrep --config=auto` against `source_root` and returns the
    parsed list of raw result dicts from Semgrep's JSON output.
    Returns an empty list (and logs) on any failure — a missing/broken
    Semgrep installation must not crash the whole scan.
    """
    command = [
        "semgrep",
        "--config=auto",
        "--no-git-ignore",
        "--json",
        "--quiet",
        "--timeout", "30",
        "--max-target-bytes", "2000000",
        str(source_root),
    ]

    try:
        result = subprocess.run(  # noqa: S603 — fixed, predefined argv; shell=False
            command,
            cwd=str(source_root),
            capture_output=True,
            text=True,
            timeout=SEMGREP_TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
    except FileNotFoundError:
        logger.warning("Semgrep is not installed / not on PATH — skipping static analysis for this scan.")
        return []
    except subprocess.TimeoutExpired:
        logger.warning("Semgrep timed out after %ss on %s", SEMGREP_TIMEOUT_SECONDS, source_root)
        return []

    if not result.stdout:
        logger.warning("Semgrep produced no output (stderr: %s)", result.stderr[:500])
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        logger.error("Semgrep output was not valid JSON")
        return []

    return payload.get("results", [])
