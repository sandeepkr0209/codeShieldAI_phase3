"""
Controlled, safe dynamic security checks.

Every check here is deliberately non-destructive: no real exploitation
payloads, no data modification, no credential access. Each check
returns normalized dynamic-observation dicts (same shape as the
static normalizer's output, but keyed on endpoint/method/parameter
instead of file/line) — NOT confirmed findings; the Security Agent
still runs RAG + LLM + verification on top of these.
"""
import re
import secrets
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.services.web_analysis.http_client import ControlledHttpClient, ProbeResult

# --- Security misconfiguration: missing headers -----------------------

RECOMMENDED_HEADERS = {
    "content-security-policy": "Content-Security-Policy",
    "x-content-type-options": "X-Content-Type-Options",
    "strict-transport-security": "Strict-Transport-Security",
    "x-frame-options": "X-Frame-Options",
}


def check_security_headers(probe: ProbeResult) -> list[dict[str, Any]]:
    if probe.error or probe.status_code is None:
        return []

    present = {k.lower() for k in probe.headers}
    missing = [label for key, label in RECOMMENDED_HEADERS.items() if key not in present]
    if not missing:
        return []

    return [
        {
            "source": "dynamic",
            "observation_type": "security_misconfiguration",
            "rule_id": "MISSING_SECURITY_HEADERS",
            "endpoint": probe.url,
            "http_method": probe.method,
            "message": f"Response is missing recommended security headers: {', '.join(missing)}.",
            "raw_severity": "MEDIUM",
            "raw_confidence": "HIGH",  # header presence/absence is a direct, deterministic observation
            "code_snippet": None,
        }
    ]


# --- Reflected XSS (harmless marker, no working payload) --------------

def _xss_marker() -> str:
    return f"cshld{secrets.token_hex(4)}"


def check_reflected_xss(client: ControlledHttpClient, url: str, param_names: list[str]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    if not param_names:
        return observations

    marker = _xss_marker()
    probe_marker = f"{marker}<xsscheck>"  # inert — no event handler, no script execution

    for param in param_names[:5]:  # cap params tested per endpoint
        test_url = _set_query_param(url, param, probe_marker)
        probe = client.get(test_url)
        if probe.error or probe.status_code is None:
            continue

        content_type = probe.headers.get("content-type", "")
        if "html" not in content_type.lower():
            continue

        # Reflected verbatim (unescaped) — a real encoding issue.
        if probe_marker in probe.body_snippet:
            observations.append(
                {
                    "source": "dynamic",
                    "observation_type": "reflected_xss_indicator",
                    "rule_id": "REFLECTED_INPUT_UNESCAPED",
                    "endpoint": url,
                    "http_method": "GET",
                    "parameter": param,
                    "message": (
                        f"Parameter '{param}' is reflected in the response without HTML encoding "
                        f"(test marker '{probe_marker}' appeared verbatim)."
                    ),
                    "raw_severity": "MEDIUM",
                    "raw_confidence": "MEDIUM",
                    "code_snippet": _extract_context(probe.body_snippet, probe_marker),
                }
            )
    return observations


# --- SQL injection error-based indicators (single quote only) ---------

_SQL_ERROR_PATTERNS = [
    r"SQL syntax.*MySQL", r"Warning.*mysqli?_", r"PostgreSQL.*ERROR", r"pg_query\(\)",
    r"SQLite3?::", r"ORA-\d{5}", r"Microsoft OLE DB Provider for SQL Server",
    r"Unclosed quotation mark", r"SQLSTATE\[",
]
_SQL_ERROR_RE = re.compile("|".join(_SQL_ERROR_PATTERNS), re.IGNORECASE)


def check_sql_injection_indicators(client: ControlledHttpClient, url: str, param_names: list[str]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    if not param_names:
        return observations

    for param in param_names[:5]:
        baseline_url = _set_query_param(url, param, "1")
        probe_url = _set_query_param(url, param, "1'")  # single quote only — no destructive payload

        baseline = client.get(baseline_url)
        probe = client.get(probe_url)
        if probe.error or probe.status_code is None:
            continue

        match = _SQL_ERROR_RE.search(probe.body_snippet)
        if match and not _SQL_ERROR_RE.search(baseline.body_snippet or ""):
            observations.append(
                {
                    "source": "dynamic",
                    "observation_type": "sql_injection_indicator",
                    "rule_id": "SQL_ERROR_BASED_INDICATOR",
                    "endpoint": url,
                    "http_method": "GET",
                    "parameter": param,
                    "message": (
                        f"Parameter '{param}' triggered a database error message when a single quote "
                        f"was appended, suggesting unsanitized input reaches a SQL query."
                    ),
                    "raw_severity": "HIGH",
                    "raw_confidence": "MEDIUM",
                    "code_snippet": _extract_context(probe.body_snippet, match.group(0)),
                }
            )
    return observations


# --- Broken access control / IDOR (comparison heuristic) --------------

_NUMERIC_ID_RE = re.compile(r"(\d+)")


def check_idor_indicator(client: ControlledHttpClient, url: str) -> list[dict[str, Any]]:
    """Only runs on URLs containing a numeric identifier. Requests the
    same endpoint with a nearby different id and flags it as a
    *potential* IDOR indicator if both return 200 with different body
    content — this is a heuristic requiring human/LLM review, not proof."""
    match = _NUMERIC_ID_RE.search(url)
    if not match:
        return []

    original_id = int(match.group(1))
    alternate_id = original_id + 1 if original_id < 10_000 else original_id - 1
    alternate_url = url[: match.start(1)] + str(alternate_id) + url[match.end(1) :]

    original = client.get(url)
    alternate = client.get(alternate_url)

    if original.error or alternate.error:
        return []
    if original.status_code != 200 or alternate.status_code != 200:
        return []
    if original.body_snippet.strip() == alternate.body_snippet.strip():
        return []  # identical response — likely not returning per-id data at all

    return [
        {
            "source": "dynamic",
            "observation_type": "idor_indicator",
            "rule_id": "IDOR_UNAUTHENTICATED_ID_VARIATION",
            "endpoint": url,
            "http_method": "GET",
            "parameter": "id",
            "message": (
                f"Requesting id={original_id} and id={alternate_id} on the same endpoint both returned "
                f"200 with different content, with no authorization check apparent from this single "
                f"unauthenticated request pattern. This is a heuristic indicator, not proof of IDOR — "
                f"verify manually whether these records should be accessible without authorization."
            ),
            "raw_severity": "MEDIUM",
            "raw_confidence": "LOW",  # explicitly low — this is the weakest of the four checks
            "code_snippet": None,
        }
    ]


# --- helpers ------------------------------------------------------------

def _set_query_param(url: str, param: str, value: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query[param] = [value]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _extract_context(body: str, needle: str, radius: int = 80) -> str:
    idx = body.find(needle)
    if idx == -1:
        return body[:200]
    start = max(0, idx - radius)
    end = min(len(body), idx + len(needle) + radius)
    return body[start:end]
