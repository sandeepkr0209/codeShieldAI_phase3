"""dynamic web analysis: web_pages, endpoints, scan counters, observation dynamic fields

Revision ID: f77516fcb3f2
Revises: 658636f084fb
Create Date: 2026-09-20 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f77516fcb3f2"
down_revision: Union[str, None] = "658636f084fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- scans: live progress counters ---
    op.add_column("scans", sa.Column("pages_discovered", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("scans", sa.Column("endpoints_discovered", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("scans", sa.Column("requests_made", sa.Integer(), nullable=False, server_default="0"))

    # --- observations: dynamic (web) location fields ---
    op.add_column("observations", sa.Column("endpoint", sa.String(2048), nullable=True))
    op.add_column("observations", sa.Column("http_method", sa.String(10), nullable=True))
    op.add_column("observations", sa.Column("parameter", sa.String(255), nullable=True))

    # --- findings: AI Security Reasoning timeline (Observation -> Hypothesis
    #     -> Test -> Evidence -> Verification -> Conclusion), JSON-encoded ---
    op.add_column("findings", sa.Column("reasoning_steps", sa.Text(), nullable=True))

    # --- web_pages ---
    op.create_table(
        "web_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("form_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("link_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_web_pages_scan_id", "web_pages", ["scan_id"])

    # --- endpoints ---
    op.create_table(
        "endpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("method", sa.String(10), nullable=False, server_default="GET"),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.Column("response_headers_json", sa.Text(), nullable=True),
        sa.Column("cookies_json", sa.Text(), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="crawler"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_endpoints_scan_id", "endpoints", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_endpoints_scan_id", table_name="endpoints")
    op.drop_table("endpoints")

    op.drop_index("ix_web_pages_scan_id", table_name="web_pages")
    op.drop_table("web_pages")

    op.drop_column("findings", "reasoning_steps")

    op.drop_column("observations", "parameter")
    op.drop_column("observations", "http_method")
    op.drop_column("observations", "endpoint")

    op.drop_column("scans", "requests_made")
    op.drop_column("scans", "endpoints_discovered")
    op.drop_column("scans", "pages_discovered")
