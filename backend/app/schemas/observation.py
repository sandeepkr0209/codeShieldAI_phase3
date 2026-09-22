"""
Pydantic schemas for Observation.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    source: str
    observation_type: str
    rule_id: str | None
    file: str | None
    line: int | None
    start_line: int | None
    end_line: int | None
    start_column: int | None
    end_column: int | None
    message: str
    raw_severity: str | None
    raw_confidence: str | None
    processed: bool
    created_at: datetime
