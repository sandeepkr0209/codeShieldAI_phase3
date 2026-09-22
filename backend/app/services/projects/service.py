"""
Project service — business logic for project CRUD, kept separate
from the API route handlers.

Ownership enforcement lives here (query-level), not just in the route
layer — every list/get function is scoped to a specific user_id so a
route can never accidentally leak another user's project by forgetting
a check. A NULL owner (legacy/pre-auth project) is visible to any
authenticated user until claimed — see app/models/project.py.
"""
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.models.project import Project
from app.models.scan import Scan


def create_project(
    db: Session, *, user_id: uuid.UUID, name: str, description: str | None, target_type, target_value: str
) -> Project:
    project = Project(
        user_id=user_id,
        name=name,
        description=description,
        target_type=target_type,
        target_value=target_value,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, *, user_id: uuid.UUID) -> list[Project]:
    stmt = (
        select(Project)
        .where(or_(Project.user_id == user_id, Project.user_id.is_(None)))
        .order_by(Project.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_project(db: Session, project_id: uuid.UUID, *, user_id: uuid.UUID) -> Project | None:
    """Returns None both when the project doesn't exist AND when it
    belongs to a different user — callers must not distinguish these
    in their response (both should 404), or they'd leak existence."""
    project = db.get(Project, project_id)
    if project is None:
        return None
    if project.user_id is not None and project.user_id != user_id:
        return None
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()


def project_scan_count(db: Session, project_id: uuid.UUID) -> int:
    stmt = select(func.count(Scan.id)).where(Scan.project_id == project_id)
    return db.execute(stmt).scalar_one()


def project_finding_count(db: Session, project_id: uuid.UUID) -> int:
    stmt = (
        select(func.count(Finding.id))
        .join(Scan, Scan.id == Finding.scan_id)
        .where(Scan.project_id == project_id)
    )
    return db.execute(stmt).scalar_one()


def project_last_scan_status(db: Session, project_id: uuid.UUID) -> str | None:
    stmt = (
        select(Scan.status)
        .where(Scan.project_id == project_id)
        .order_by(Scan.created_at.desc())
        .limit(1)
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result.value if result else None
