"""
Finding model.

A Finding represents a potential security issue or code-quality problem.
Severity (impact) and confidence (evidence strength) are kept as two
separate, independent dimensions per the project's evidence-driven design.

`verified` / `verification_method` / `verification_reason` are populated
by the deterministic Verification engine (services/security_agent/verifier.py)
— NOT by raw LLM confidence — per the project's evidence-driven principle.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Severity(str, enum.Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(str, enum.Enum):
    POTENTIAL = "potential"  # observation -> LLM explanation, not yet verified
    CONFIRMED = "confirmed"  # passed the deterministic Verification engine
    OPEN = "open"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"
    RESOLVED = "resolved"


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="finding_severity", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 - 1.0

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Source location (never fabricated — null when an analyzer can't provide one) ---
    file: Mapped[str | None] = mapped_column(String(512), nullable=True)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)  # kept for backward compat (== start_line)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_column: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_column: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Dynamic-finding location (Phase 5 — nullable, unused for source findings) ---
    endpoint: Mapped[str | None] = mapped_column(String(512), nullable=True)
    http_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    parameter: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Analyzer provenance ---
    analyzer: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "semgrep" | "bandit" | "dynamic"
    rule_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    cwe_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    owasp_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # --- Verification (deterministic — see services/security_agent/verifier.py) ---
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verification_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON-encoded list of {label, text} steps: Observation -> Hypothesis ->
    # Test -> Evidence -> Verification -> Conclusion. Populated by
    # SecurityAgent.create_finding() — powers the "AI Security Reasoning"
    # timeline in the finding detail UI. Never null for agent-generated findings.
    reasoning_steps: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus, name="finding_status", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=FindingStatus.POTENTIAL,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scan: Mapped["Scan"] = relationship("Scan", back_populates="findings")
    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="finding", cascade="all, delete-orphan"
    )
