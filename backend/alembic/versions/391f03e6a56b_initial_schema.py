"""initial schema: projects, scans, findings, evidence, reports

Revision ID: 391f03e6a56b
Revises:
Create Date: 2026-09-17 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "391f03e6a56b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    target_type = postgresql.ENUM("website", "github", "zip", name="target_type")
    scan_status = postgresql.ENUM("pending", "running", "completed", "failed", name="scan_status")
    scan_type = postgresql.ENUM("source_code", "web_application", name="scan_type")
    finding_severity = postgresql.ENUM(
        "informational", "low", "medium", "high", "critical", name="finding_severity"
    )
    finding_status = postgresql.ENUM(
        "open", "confirmed", "false_positive", "resolved", name="finding_status"
    )

    bind = op.get_bind()
    target_type.create(bind, checkfirst=True)
    scan_status.create(bind, checkfirst=True)
    scan_type.create(bind, checkfirst=True)
    finding_severity.create(bind, checkfirst=True)
    finding_status.create(bind, checkfirst=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_type", target_type, nullable=False),
        sa.Column("target_value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", scan_status, nullable=False, server_default="pending"),
        sa.Column("scan_type", scan_type, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("severity", finding_severity, nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file", sa.String(512), nullable=True),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("endpoint", sa.String(512), nullable=True),
        sa.Column("parameter", sa.String(255), nullable=True),
        sa.Column("impact", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("cwe_id", sa.String(50), nullable=True),
        sa.Column("owasp_category", sa.String(100), nullable=True),
        sa.Column("status", finding_status, nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "finding_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("findings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("evidence_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("report_type", sa.String(50), nullable=False, server_default="html"),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("evidence")
    op.drop_table("findings")
    op.drop_table("scans")
    op.drop_table("projects")

    bind = op.get_bind()
    postgresql.ENUM(name="finding_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="finding_severity").drop(bind, checkfirst=True)
    postgresql.ENUM(name="scan_type").drop(bind, checkfirst=True)
    postgresql.ENUM(name="scan_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="target_type").drop(bind, checkfirst=True)
