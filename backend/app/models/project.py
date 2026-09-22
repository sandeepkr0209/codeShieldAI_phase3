"""
Project model.

A Project represents something the user wants to analyze:
a website, a GitHub repository, or an uploaded ZIP of source code.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TargetType(str, enum.Enum):
    WEBSITE = "website"
    GITHUB = "github"
    ZIP = "zip"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Nullable: existing projects created before authentication was added
    # have no owner. They are NOT deleted (see migration) — ownership
    # checks treat a NULL owner as "legacy/unclaimed", visible to any
    # authenticated user, rather than silently destroying pre-auth data.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    target_type: Mapped[TargetType] = mapped_column(
        Enum(TargetType, name="target_type", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    target_value: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    scans: Mapped[list["Scan"]] = relationship(
        "Scan", back_populates="project", cascade="all, delete-orphan"
    )
    source_files: Mapped[list["SourceFile"]] = relationship(
        "SourceFile", back_populates="project", cascade="all, delete-orphan"
    )
