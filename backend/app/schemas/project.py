"""
Pydantic schemas for Project CRUD.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.project import TargetType


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    target_type: TargetType
    target_value: str = Field(..., min_length=1)

    @field_validator("target_type", mode="before")
    @classmethod
    def _normalize_target_type(cls, value):
        # Accept any casing (e.g. "GITHUB", "GitHub") since the DB enum
        # itself is lowercase-only — avoids a confusing 500 from Postgres
        # when someone types the value by hand (e.g. in /docs).
        if isinstance(value, str):
            return value.strip().lower()
        return value


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    target_type: TargetType
    target_value: str
    created_at: datetime
    updated_at: datetime


class ProjectSummary(ProjectRead):
    """Project with lightweight aggregate counts for list views."""

    scan_count: int = 0
    finding_count: int = 0
    last_scan_status: str | None = None
