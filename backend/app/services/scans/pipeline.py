"""
Source-code scan pipeline orchestrator.

  Dependency check -> Ingestion -> Parsing -> Static Analysis ->
  Observation normalization -> Security Agent (RAG + LLM + Verification)
  -> Findings -> Complete

Runs as a FastAPI BackgroundTask (see api/routes/scans.py) — no
Celery/Redis, per the project's "don't over-engineer" principle. Each
run gets its own DB session since the request-scoped session is
already closed by the time this executes.
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.db.database import SessionLocal
from app.models.project import Project
from app.models.scan import Scan, ScanStage, ScanStatus
from app.models.source_file import SourceFile
from app.services.code_analysis.bandit_runner import run_bandit
from app.services.code_analysis.language_detector import detect_language
from app.services.code_analysis.normalizer import normalize_bandit_results, normalize_semgrep_results
from app.services.code_analysis.semgrep_runner import run_semgrep
from app.services.code_analysis.tree_sitter_parser import extract_structure
from app.services.code_analysis.zip_extractor import sha256_of_file
from app.services.security_agent.agent import SecurityAgent
from app.services.security_agent.dependency_check import build_warning_string, check_analyzer_availability

logger = logging.getLogger(__name__)

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "projects"


def project_source_root(project_id: UUID) -> Path:
    return STORAGE_ROOT / str(project_id) / "source"


def _set_stage(db, scan: Scan, stage: ScanStage) -> None:
    scan.current_stage = stage.value
    db.commit()


def run_source_scan(scan_id: UUID) -> None:
    """Entry point invoked as a background task. Owns its own DB session."""
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None:
            logger.error("run_source_scan: scan %s not found", scan_id)
            return

        project = db.get(Project, scan.project_id)
        source_root = project_source_root(project.id)

        if not source_root.exists() or not any(source_root.iterdir()):
            scan.status = ScanStatus.FAILED
            scan.current_stage = ScanStage.FAILED.value
            scan.error_message = (
                "No source code found for this project. Upload a ZIP or import a "
                "GitHub repository before starting a source-code scan."
            )
            db.commit()
            return

        # --- Dependency validation (Group 1): check tool availability BEFORE
        # claiming any analysis happened, and record it on the scan so the UI
        # can honestly distinguish "completed" from "completed with limited
        # analysis" rather than silently skipping a missing tool.
        availability = check_analyzer_availability()
        scan.warnings = build_warning_string(availability)
        logger.info("Scan %s analyzer availability: %s", scan_id, availability)

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.now(timezone.utc)
        db.commit()

        _run_pipeline(db, scan, project, source_root, availability)

    except Exception as exc:  # noqa: BLE001 — a failed scan must be recorded, not crash the worker
        logger.exception("Scan %s failed", scan_id)
        try:
            scan = db.get(Scan, scan_id)
            if scan is not None:
                scan.status = ScanStatus.FAILED
                scan.current_stage = ScanStage.FAILED.value
                scan.error_message = str(exc)[:2000]
                db.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to record scan failure for %s", scan_id)
    finally:
        db.close()


def _run_pipeline(db, scan: Scan, project: Project, source_root: Path, availability: dict[str, bool]) -> None:
    # --- Stage: EXTRACTING (create a fresh SourceFile snapshot for this scan) ---
    _set_stage(db, scan, ScanStage.EXTRACTING)
    source_files = _index_source_files(db, project.id, scan.id, source_root)

    # --- Stage: PARSING (Tree-sitter structural extraction) ---
    _set_stage(db, scan, ScanStage.PARSING)
    if availability.get("tree_sitter"):
        for sf in source_files:
            structure = extract_structure(source_root / sf.path, sf.language)
            sf.function_count = len(structure["functions"])
            sf.class_count = len(structure["classes"])
        db.commit()
    else:
        logger.warning("Scan %s: tree-sitter unavailable, skipping structural parsing", scan.id)

    # --- Stage: STATIC_ANALYSIS (Semgrep + Bandit) ---
    _set_stage(db, scan, ScanStage.STATIC_ANALYSIS)
    observations = _run_static_analysis(db, scan.id, source_root, availability)

    # --- Stage: AI_ANALYSIS (Security Agent: prioritize -> hypothesis ->
    #     RAG -> LLM -> verify -> finding, for each observation) ---
    _set_stage(db, scan, ScanStage.AI_ANALYSIS)
    languages_present = {sf.language for sf in source_files if sf.language}
    primary_language = next(iter(languages_present), None)
    _run_security_agent(db, observations, primary_language)

    # --- Stage: COMPLETED ---
    scan.status = ScanStatus.COMPLETED
    scan.current_stage = ScanStage.COMPLETED.value
    scan.completed_at = datetime.now(timezone.utc)
    db.commit()


def _index_source_files(db, project_id: UUID, scan_id: UUID, source_root: Path):
    records = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        language = detect_language(path)
        record = SourceFile(
            project_id=project_id,
            scan_id=scan_id,
            path=str(path.relative_to(source_root)),
            language=language,
            size=path.stat().st_size,
            file_hash=sha256_of_file(path),
        )
        db.add(record)
        records.append(record)
    db.commit()
    for r in records:
        db.refresh(r)
    return records


def _run_static_analysis(db, scan_id: UUID, source_root: Path, availability: dict[str, bool]):
    semgrep_raw = run_semgrep(source_root) if availability.get("semgrep") else []
    bandit_raw = run_bandit(source_root) if availability.get("bandit") else []

    normalized = normalize_semgrep_results(semgrep_raw, source_root) + normalize_bandit_results(
        bandit_raw, source_root
    )

    from app.models.observation import Observation

    observations = []
    for item in normalized:
        obs = Observation(scan_id=scan_id, **item)
        db.add(obs)
        observations.append(obs)
    db.commit()
    for o in observations:
        db.refresh(o)

    logger.info(
        "Scan %s: %d Semgrep + %d Bandit raw results -> %d normalized observations",
        scan_id, len(semgrep_raw), len(bandit_raw), len(observations),
    )
    return observations


def _run_security_agent(db, observations, language: str | None) -> None:
    agent = SecurityAgent(db)
    prioritized = agent.prioritize(agent.observe(observations))

    confirmed = 0
    for obs in prioritized:
        try:
            result = agent.run_for_observation(obs, language)
            if result.verified:
                confirmed += 1
        except Exception:  # noqa: BLE001 — one bad observation must not abort the whole scan
            logger.exception("Security Agent failed on observation %s — skipping", obs.id)

    logger.info(
        "Security Agent processed %d observations -> %d confirmed findings", len(prioritized), confirmed
    )
