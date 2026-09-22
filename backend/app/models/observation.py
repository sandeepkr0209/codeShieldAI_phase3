"""
Observation model.

An Observation is a raw, unverified signal from a deterministic tool
(Semgrep, Bandit, or the dynamic checks in services/web_analysis/) —
it is NOT automatically a confirmed vulnerability. The Finding it may
produce carries a `status` of "potential" until reviewed, distinguishing
tool output from a vetted security finding.

`file`/`line*` apply to static (source-code) observations;
`endpoint`/`http_method`/`parameter` apply to dynamic (web) ones —
each observation only ever populates the set relevant to its source.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )

    source: Mapped[str] = mapped_column(String(50), nullable=False)  # "semgrep" | "bandit" | "dynamic"
    observation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="static_analysis")
    rule_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Static (source-code) location
    file: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)  # kept for backward compat (== start_line)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_column: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_column: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Dynamic (web) location
    endpoint: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    http_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    parameter: Mapped[str | None] = mapped_column(String(255), nullable=True)

    message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_confidence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    processed: Mapped[bool] = mapped_column(nullable=False, default=False)  # whether RAG+LLM has run on this yet

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scan: Mapped["Scan"] = relationship("Scan", back_populates="observations")
