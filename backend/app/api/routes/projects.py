"""
Project API routes. All require authentication; every read/write is
scoped to the current user (see services/projects/service.py).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectSummary
from app.services.projects import service as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProjectRead:
    project = project_service.create_project(
        db,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        target_type=payload.target_type,
        target_value=payload.target_value,
    )
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectSummary])
def list_projects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ProjectSummary]:
    projects = project_service.list_projects(db, user_id=current_user.id)
    summaries = []
    for project in projects:
        summaries.append(
            ProjectSummary(
                **ProjectRead.model_validate(project).model_dump(),
                scan_count=project_service.project_scan_count(db, project.id),
                finding_count=project_service.project_finding_count(db, project.id),
                last_scan_status=project_service.project_last_scan_status(db, project.id),
            )
        )
    return summaries


@router.get("/{project_id}", response_model=ProjectSummary)
def get_project(
    project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProjectSummary:
    project = project_service.get_project(db, project_id, user_id=current_user.id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectSummary(
        **ProjectRead.model_validate(project).model_dump(),
        scan_count=project_service.project_scan_count(db, project.id),
        finding_count=project_service.project_finding_count(db, project.id),
        last_scan_status=project_service.project_last_scan_status(db, project.id),
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    project = project_service.get_project(db, project_id, user_id=current_user.id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project_service.delete_project(db, project)
