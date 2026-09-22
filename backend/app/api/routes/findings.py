"""
Finding API routes (direct retrieval by id, with evidence). Ownership
is checked through finding -> scan -> project -> user.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.finding import FindingDetail
from app.services.findings import service as finding_service
from app.services.projects import service as project_service
from app.services.scans import service as scan_service

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/{finding_id}", response_model=FindingDetail)
def get_finding(
    finding_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> FindingDetail:
    finding = finding_service.get_finding(db, finding_id)
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    scan = scan_service.get_scan(db, finding.scan_id)
    if scan is None or project_service.get_project(db, scan.project_id, user_id=current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    return FindingDetail.model_validate(finding)
