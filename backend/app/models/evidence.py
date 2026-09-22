"""
Evidence model.

Evidence is stored separately from generated explanations so that
what was actually observed/detected is never conflated with the
LLM's interpretation of it.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False
    )

    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "static_analysis", "http_response"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. "semgrep", "bandit", "httpx"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    finding: Mapped["Finding"] = relationship("Finding", back_populates="evidence")
