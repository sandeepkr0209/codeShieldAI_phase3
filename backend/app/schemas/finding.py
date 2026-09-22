"""
Pydantic schemas for Finding and Evidence.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.finding import FindingStatus, Severity


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evidence_type: str
    content: str
    source: str | None
    created_at: datetime


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    title: str
    category: str
    severity: Severity
    confidence: float
    description: str | None

    file: str | None
    line: int | None
    start_line: int | None
    end_line: int | None
    start_column: int | None
    end_column: int | None
    code_snippet: str | None

    endpoint: str | None
    http_method: str | None
    parameter: str | None

    analyzer: str | None
    rule_id: str | None

    impact: str | None
    recommendation: str | None
    cwe_id: str | None
    owasp_category: str | None

    verified: bool
    verification_method: str | None
    verification_reason: str | None
    reasoning_steps: str | None  # JSON-encoded [{label, text}, ...] — see SecurityAgent.build_reasoning_steps

    status: FindingStatus
    created_at: datetime


class FindingDetail(FindingRead):
    evidence: list[EvidenceRead] = []
