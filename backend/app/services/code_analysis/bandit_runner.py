"""
Controlled Bandit execution (Python security linting).

Same safety posture as semgrep_runner.py: fixed argv, no shell=True,
hard timeout, restricted working directory.
"""
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

BANDIT_TIMEOUT_SECONDS = 120


def run_bandit(source_root: Path) -> list[dict[str, Any]]:
    """
    Runs `bandit -r <source_root> -f json` and returns the parsed list
    of raw result dicts. Returns an empty list on any failure.
    """
    command = ["bandit", "-r", str(source_root), "-f", "json", "-q"]

    try:
        result = subprocess.run(  # noqa: S603 — fixed, predefined argv; shell=False
            command,
            cwd=str(source_root),
            capture_output=True,
            text=True,
            timeout=BANDIT_TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
    except FileNotFoundError:
        logger.warning("Bandit is not installed / not on PATH — skipping Python security lint for this scan.")
        return []
    except subprocess.TimeoutExpired:
        logger.warning("Bandit timed out after %ss on %s", BANDIT_TIMEOUT_SECONDS, source_root)
        return []

    if not result.stdout:
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        logger.error("Bandit output was not valid JSON")
        return []

    return payload.get("results", [])
