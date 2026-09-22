"""
Pydantic schemas for SourceFile.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    path: str
    language: str | None
    size: int
    function_count: int
    class_count: int
    created_at: datetime


class SourceUploadResponse(BaseModel):
    files_ingested: int
    total_size_bytes: int
    languages: dict[str, int]  # language -> file count


class GitHubImportRequest(BaseModel):
    repo_url: str
