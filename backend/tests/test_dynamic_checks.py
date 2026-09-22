from unittest.mock import MagicMock
from urllib.parse import parse_qs, unquote, urlparse

from app.services.web_analysis import dynamic_checks
from app.services.web_analysis.http_client import ProbeResult


def _probe(**overrides) -> ProbeResult:
    defaults = dict(
        url="http://example.com/page",
        method="GET",
        status_code=200,
        headers={"content-type": "text/html"},
        cookies=[],
        body_snippet="<html><body>hello</body></html>",
        elapsed_ms=10.0,
    )
    defaults.update(overrides)
    return ProbeResult(**defaults)


def test_missing_security_headers_flagged():
    probe = _probe(headers={"content-type": "text/html"})
    observations = dynamic_checks.check_security_headers(probe)
    assert len(observations) == 1
    assert observations[0]["rule_id"] == "MISSING_SECURITY_HEADERS"
    assert observations[0]["raw_confidence"] == "HIGH"


def test_all_security_headers_present_no_finding():
    probe = _probe(
        headers={
            "content-type": "text/html",
            "content-security-policy": "default-src 'self'",
            "x-content-type-options": "nosniff",
            "strict-transport-security": "max-age=63072000",
            "x-frame-options": "DENY",
        }
    )
    assert dynamic_checks.check_security_headers(probe) == []


def test_reflected_xss_detected_when_marker_unescaped():
    client = MagicMock()

    def fake_get(url):
        # Simulate a vulnerable app: it URL-decodes the query param and
        # echoes it into the HTML body verbatim, unescaped.
        query = parse_qs(urlparse(url).query)
        reflected = unquote(query.get("q", [""])[0])
        return _probe(body_snippet=f"<html>you searched for: {reflected}</html>")

    client.get.side_effect = fake_get

    observations = dynamic_checks.check_reflected_xss(client, "http://example.com/search", ["q"])
    assert len(observations) == 1
    assert observations[0]["rule_id"] == "REFLECTED_INPUT_UNESCAPED"
    assert observations[0]["parameter"] == "q"


def test_reflected_xss_none_when_no_params():
    client = MagicMock()
    assert dynamic_checks.check_reflected_xss(client, "http://example.com/", []) == []


def test_sql_injection_indicator_detected():
    client = MagicMock()

    def fake_get(url):
        if "%27" in url or "'" in url:
            return _probe(body_snippet="Warning: mysqli_query(): You have an error in your SQL syntax")
        return _probe(body_snippet="<html>normal page</html>")

    client.get.side_effect = fake_get
    observations = dynamic_checks.check_sql_injection_indicators(client, "http://example.com/item", ["id"])
    assert len(observations) == 1
    assert observations[0]["rule_id"] == "SQL_ERROR_BASED_INDICATOR"


def test_sql_injection_indicator_none_when_no_error():
    client = MagicMock()
    client.get.return_value = _probe(body_snippet="<html>normal page, no errors</html>")
    observations = dynamic_checks.check_sql_injection_indicators(client, "http://example.com/item", ["id"])
    assert observations == []


def test_idor_indicator_flagged_on_differing_responses():
    client = MagicMock()

    def fake_get(url):
        if "id=1" in url or url.endswith("/1"):
            return _probe(body_snippet="user: alice")
        return _probe(body_snippet="user: bob")

    client.get.side_effect = fake_get
    observations = dynamic_checks.check_idor_indicator(client, "http://example.com/users/1")
    assert len(observations) == 1
    assert observations[0]["raw_confidence"] == "LOW"  # explicitly weak heuristic


def test_idor_indicator_skipped_without_numeric_id():
    client = MagicMock()
    assert dynamic_checks.check_idor_indicator(client, "http://example.com/dashboard") == []


def test_idor_indicator_none_when_responses_identical():
    client = MagicMock()
    client.get.return_value = _probe(body_snippet="same content regardless of id")
    observations = dynamic_checks.check_idor_indicator(client, "http://example.com/users/1")
    assert observations == []
