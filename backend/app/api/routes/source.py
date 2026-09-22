"""
Source ingestion routes: ZIP upload and GitHub repository import.

Both write extracted files under storage/projects/{project_id}/source/
and create project-level SourceFile records (scan_id=None at this
point — a fresh scan-scoped snapshot is created when a scan actually
runs, see services/scans/pipeline.py).
"""
import logging
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.source_file import SourceFile
from app.models.user import User
from app.schemas.source_file import GitHubImportRequest, SourceFileRead, SourceUploadResponse
from app.services.code_analysis.language_detector import detect_language
from app.services.code_analysis.zip_extractor import (
    MAX_ARCHIVE_BYTES,
    UnsafeArchiveError,
    extract_zip_safely,
    sha256_of_file,
)
from app.services.scans.pipeline import project_source_root
from app.services.source_ingestion.github import GitHubIngestionError, download_and_extract_repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["source"])


def _get_owned_project_or_404(db: Session, project_id: uuid.UUID, user: User) -> Project:
    from app.services.projects.service import get_project as get_owned_project

    project = get_owned_project(db, project_id, user_id=user.id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _replace_project_source_files(db: Session, project_id: uuid.UUID, extracted_paths: list[Path], source_root: Path) -> SourceUploadResponse:
    # Clear any previous project-level source file index before re-indexing.
    db.query(SourceFile).filter(SourceFile.project_id == project_id, SourceFile.scan_id.is_(None)).delete()

    languages: dict[str, int] = {}
    total_size = 0
    for path in extracted_paths:
        if not path.is_file():
            continue
        language = detect_language(path)
        size = path.stat().st_size
        total_size += size
        if language:
            languages[language] = languages.get(language, 0) + 1

        db.add(
            SourceFile(
                project_id=project_id,
                scan_id=None,
                path=str(path.relative_to(source_root)),
                language=language,
                size=size,
                file_hash=sha256_of_file(path),
            )
        )
    db.commit()

    return SourceUploadResponse(files_ingested=len(extracted_paths), total_size_bytes=total_size, languages=languages)


@router.post("/{project_id}/source/upload", response_model=SourceUploadResponse)
async def upload_source_zip(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SourceUploadResponse:
    project = _get_owned_project_or_404(db, project_id, current_user)

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .zip files are accepted")

    source_root = project_source_root(project.id)
    if source_root.exists():
        shutil.rmtree(source_root)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp_path = Path(tmp.name)
        size = 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_ARCHIVE_BYTES:
                tmp_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Archive exceeds the {MAX_ARCHIVE_BYTES // (1024 * 1024)}MB limit",
                )
            tmp.write(chunk)

    try:
        extracted = extract_zip_safely(tmp_path, source_root)
    except UnsafeArchiveError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    if not extracted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No usable files found in the archive (all entries were ignored or too large)",
        )

    return _replace_project_source_files(db, project.id, extracted, source_root)


@router.post("/{project_id}/source/github", response_model=SourceUploadResponse)
def import_github_repo(
    project_id: uuid.UUID,
    payload: GitHubImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SourceUploadResponse:
    project = _get_owned_project_or_404(db, project_id, current_user)

    source_root = project_source_root(project.id)
    if source_root.exists():
        shutil.rmtree(source_root)

    try:
        extracted = download_and_extract_repo(payload.repo_url, source_root)
    except GitHubIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not extracted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No usable files found in the repository")

    return _replace_project_source_files(db, project.id, extracted, source_root)


@router.get("/{project_id}/source-files", response_model=list[SourceFileRead])
def list_source_files(
    project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[SourceFileRead]:
    _get_owned_project_or_404(db, project_id, current_user)
    stmt = (
        select(SourceFile)
        .where(SourceFile.project_id == project_id, SourceFile.scan_id.is_(None))
        .order_by(SourceFile.path)
    )
    files = list(db.execute(stmt).scalars().all())
    return [SourceFileRead.model_validate(f) for f in files]
