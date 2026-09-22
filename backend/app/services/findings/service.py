"""
Finding service — read-only in Phase 1 since no analysis engine
produces findings yet. Provided so routes don't query the ORM directly.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.finding import Finding


def list_findings_for_scan(db: Session, scan_id: uuid.UUID) -> list[Finding]:
    stmt = select(Finding).where(Finding.scan_id == scan_id).order_by(Finding.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_finding(db: Session, finding_id: uuid.UUID) -> Finding | None:
    stmt = (
        select(Finding)
        .where(Finding.id == finding_id)
        .options(selectinload(Finding.evidence))
    )
    return db.execute(stmt).scalar_one_or_none()
