"""phase 2: source_files, observations, scan progress columns, potential finding status

Revision ID: 8ede5694c63f
Revises: 391f03e6a56b
Create Date: 2026-09-18 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8ede5694c63f"
down_revision: Union[str, None] = "391f03e6a56b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- scans: granular progress tracking ---
    op.add_column("scans", sa.Column("current_stage", sa.String(50), nullable=True))
    op.add_column("scans", sa.Column("error_message", sa.String(2048), nullable=True))

    # --- findings: add "potential" status (observation -> LLM explanation,
    #     not yet human/rule-confirmed). Must commit before it can be used
    #     in an INSERT/UPDATE, but this migration only adds the value.
    op.execute("ALTER TYPE finding_status ADD VALUE IF NOT EXISTS 'potential'")

    # --- source_files ---
    op.create_table(
        "source_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("path", sa.String(1024), nullable=False),
        sa.Column("language", sa.String(50), nullable=True),
        sa.Column("size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("function_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("class_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_source_files_project_id", "source_files", ["project_id"])
    op.create_index("ix_source_files_scan_id", "source_files", ["scan_id"])

    # --- observations ---
    op.create_table(
        "observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("observation_type", sa.String(50), nullable=False, server_default="static_analysis"),
        sa.Column("rule_id", sa.String(255), nullable=True),
        sa.Column("file", sa.String(1024), nullable=True),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("raw_severity", sa.String(50), nullable=True),
        sa.Column("raw_confidence", sa.String(50), nullable=True),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_observations_scan_id", "observations", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_observations_scan_id", table_name="observations")
    op.drop_table("observations")

    op.drop_index("ix_source_files_scan_id", table_name="source_files")
    op.drop_index("ix_source_files_project_id", table_name="source_files")
    op.drop_table("source_files")

    # Note: PostgreSQL does not support removing a value from an enum
    # type. Downgrading leaves 'potential' in finding_status — this is
    # a known, documented limitation of the downgrade path.

    op.drop_column("scans", "error_message")
    op.drop_column("scans", "current_stage")
