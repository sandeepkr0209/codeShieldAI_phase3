"""
Scan service — business logic for scan lifecycle records.

Phase 1 only creates and reads scan *records*. No actual analysis
engine is invoked yet (that begins in Phase 2 for source code and
Phase 5 for web applications).
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.models.scan import Scan, ScanStatus


def create_scan(db: Session, *, project_id: uuid.UUID, scan_type) -> Scan:
    scan = Scan(project_id=project_id, scan_type=scan_type, status=ScanStatus.PENDING)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def list_scans_for_project(db: Session, project_id: uuid.UUID) -> list[Scan]:
    stmt = select(Scan).where(Scan.project_id == project_id).order_by(Scan.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_scan(db: Session, scan_id: uuid.UUID) -> Scan | None:
    return db.get(Scan, scan_id)


def scan_finding_count(db: Session, scan_id: uuid.UUID) -> int:
    stmt = select(func.count(Finding.id)).where(Finding.scan_id == scan_id)
    return db.execute(stmt).scalar_one()
