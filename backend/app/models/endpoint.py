"""
Endpoint model.

Represents one discovered API/route/form-target endpoint — the
"routes/APIs" part of the application map. Parameters, headers, and
cookies are stored as JSON-encoded strings (kept simple/inspectable
rather than introducing separate child tables for a 7th-semester
project's scope).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )

    method: Mapped[str] = mapped_column(String(10), nullable=False, default="GET")
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of param names
    # Response headers actually observed — sensitive ones (Set-Cookie,
    # Authorization) are redacted before storage; see dynamic_checks.py.
    response_headers_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    cookies_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # names only, never values
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="crawler")  # "crawler" | "form"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scan: Mapped["Scan"] = relationship("Scan", back_populates="endpoints")
