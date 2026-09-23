"""
Web-application scan pipeline orchestrator.

  Scope validation -> Reconnaissance (crawl) -> Application mapping
  -> Security testing (controlled dynamic checks) -> Security Agent
  (RAG + LLM + Verification, same as the source-code pipeline) -> Complete

Degrades gracefully: if Playwright isn't available, reconnaissance
falls back to testing just the target URL itself via HTTPX rather than
failing the whole scan — recorded as a warning, never silently.
"""
import logging
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import UUID

from app.db.database import SessionLocal
from app.models.endpoint import Endpoint
from app.models.observation import Observation
from app.models.project import Project
from app.models.scan import Scan, ScanStage, ScanStatus
from app.models.web_page import WebPage
from app.services.security_agent.agent import SecurityAgent
from app.services.security_agent.dependency_check import build_warning_string, check_analyzer_availability
from app.services.web_analysis import dynamic_checks
from app.services.web_analysis.crawler import crawl, is_playwright_available
from app.services.web_analysis.http_client import ControlledHttpClient
from app.services.web_analysis.scope import ScopeValidationError, validate_target

logger = logging.getLogger(__name__)

# Bound how many endpoints get the full (headers + XSS + SQLi + IDOR)
# check suite, so a large site with many discovered endpoints can't
# blow the scan duration budget.
MAX_ENDPOINTS_TESTED = 20


def _set_stage(db, scan: Scan, stage: ScanStage) -> None:
    scan.current_stage = stage.value
    db.commit()


async def run_web_scan(scan_id: UUID) -> None:
    """Entry point invoked as a background task. Owns its own DB session."""
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None:
            logger.error("run_web_scan: scan %s not found", scan_id)
            return

        project = db.get(Project, scan.project_id)

        availability = check_analyzer_availability()
        scan.warnings = build_warning_string(availability)

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.now(timezone.utc)
        db.commit()

        await _run_pipeline(db, scan, project, availability)

    except Exception as exc:  # noqa: BLE001
        logger.exception("Web scan %s failed", scan_id)
        try:
            scan = db.get(Scan, scan_id)
            if scan is not None:
                scan.status = ScanStatus.FAILED
                scan.current_stage = ScanStage.FAILED.value
                scan.error_message = str(exc)[:2000]
                db.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to record web scan failure for %s", scan_id)
    finally:
        db.close()


async def _run_pipeline(db, scan: Scan, project: Project, availability: dict) -> None:
    # --- Stage: SCOPE_VALIDATION ---
    _set_stage(db, scan, ScanStage.SCOPE_VALIDATION)
    try:
        scope = validate_target(project.target_value)
    except ScopeValidationError as exc:
        scan.status = ScanStatus.FAILED
        scan.current_stage = ScanStage.FAILED.value
        scan.error_message = f"Scope validation failed: {exc}"
        db.commit()
        return

    # --- Stage: RECONNAISSANCE ---
    _set_stage(db, scan, ScanStage.RECONNAISSANCE)
    if is_playwright_available():
        crawl_result = await asyncio.to_thread(crawl, scope)
    else:
        crawl_result = None
        logger.warning("Scan %s: Playwright unavailable — falling back to single-URL analysis", scan.id)

    if crawl_result and crawl_result.pages:
        for page in crawl_result.pages:
            db.add(
                WebPage(
                    scan_id=scan.id,
                    url=page.url,
                    title=page.title,
                    status_code=page.status_code,
                    form_count=len(page.forms),
                    link_count=len(page.links),
                )
            )
        scan.pages_discovered = len(crawl_result.pages)
        db.commit()
    else:
        # Graceful fallback: treat the target URL itself as the one page.
        db.add(WebPage(scan_id=scan.id, url=scope.target_url, title=None, status_code=None))
        scan.pages_discovered = 1
        db.commit()

    # --- Stage: APPLICATION_MAPPING (build the Endpoint list) ---
    _set_stage(db, scan, ScanStage.APPLICATION_MAPPING)
    endpoints = _build_endpoint_list(crawl_result, scope)
    for method, url, params in endpoints:
        db.add(Endpoint(scan_id=scan.id, method=method, url=url, parameters_json=_json(params), source="crawler"))
    scan.endpoints_discovered = len(endpoints)
    db.commit()

    # --- Stage: SECURITY_TESTING (controlled dynamic checks) ---
    _set_stage(db, scan, ScanStage.SECURITY_TESTING)
    client = ControlledHttpClient(scope)
    try:
        observations = _run_dynamic_checks(db, scan.id, client, endpoints[:MAX_ENDPOINTS_TESTED])
    finally:
        scan.requests_made = client.request_count
        db.commit()
        client.close()

    # --- Stage: EVIDENCE_COLLECTION + VERIFICATION (Security Agent) ---
    _set_stage(db, scan, ScanStage.EVIDENCE_COLLECTION)
    _run_security_agent(db, observations)

    # --- Stage: COMPLETED ---
    scan.status = ScanStatus.COMPLETED
    scan.current_stage = ScanStage.COMPLETED.value
    scan.completed_at = datetime.now(timezone.utc)
    db.commit()


def _build_endpoint_list(crawl_result, scope) -> list[tuple[str, str, list[str]]]:
    """Returns [(method, url, param_names), ...], deduplicated."""
    seen: set[tuple[str, str]] = set()
    endpoints: list[tuple[str, str, list[str]]] = []

    def add(method: str, url: str, params: list[str]) -> None:
        key = (method.upper(), url)
        if key in seen or not scope.is_url_in_scope(url):
            return
        seen.add(key)
        endpoints.append((method.upper(), url, params))

    if crawl_result:
        for page in crawl_result.pages:
            add("GET", page.url, _parse_query_names(page.url))
            for form in page.forms:
                add(form.method, form.action_url, form.input_names)
    else:
        add("GET", scope.target_url, _parse_query_names(scope.target_url))

    return endpoints


def _parse_query_names(url: str) -> list[str]:
    from urllib.parse import parse_qs

    return list(parse_qs(urlparse(url).query).keys())


def _run_dynamic_checks(db, scan_id: UUID, client: ControlledHttpClient, endpoints) -> list[Observation]:
    raw_observations: list[dict] = []

    for method, url, params in endpoints:
        probe = client.get(url) if method == "GET" else None
        if probe:
            raw_observations.extend(dynamic_checks.check_security_headers(probe))
        if method == "GET" and params:
            raw_observations.extend(dynamic_checks.check_reflected_xss(client, url, params))
            raw_observations.extend(dynamic_checks.check_sql_injection_indicators(client, url, params))
        if method == "GET":
            raw_observations.extend(dynamic_checks.check_idor_indicator(client, url))

    observations: list[Observation] = []
    for item in raw_observations:
        obs = Observation(scan_id=scan_id, **item)
        db.add(obs)
        observations.append(obs)
    db.commit()
    for o in observations:
        db.refresh(o)

    logger.info("Scan %s: dynamic checks produced %d observations", scan_id, len(observations))
    return observations


def _run_security_agent(db, observations: list[Observation]) -> None:
    agent = SecurityAgent(db)
    prioritized = agent.prioritize(agent.observe(observations))

    confirmed = 0
    for obs in prioritized:
        try:
            result = agent.run_for_observation(obs, language=None)
            if result.verified:
                confirmed += 1
        except Exception:  # noqa: BLE001
            logger.exception("Security Agent failed on dynamic observation %s — skipping", obs.id)

    logger.info("Security Agent processed %d dynamic observations -> %d confirmed findings", len(prioritized), confirmed)


def _json(value) -> str:
    import json

    return json.dumps(value)
