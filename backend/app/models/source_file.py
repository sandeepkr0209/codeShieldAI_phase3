"""
SourceFile model.

Represents one file extracted from an uploaded ZIP or imported GitHub
repository. The actual file content is NOT stored in PostgreSQL —
only a reference to its location on local disk under storage/ — to
avoid bloating the database with large source blobs.
"""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    scan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=True
    )

    path: Mapped[str] = mapped_column(String(1024), nullable=False)  # relative path within the project source root
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # sha256
    function_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    class_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="source_files")
    scan: Mapped["Scan"] = relationship("Scan", back_populates="source_files")
