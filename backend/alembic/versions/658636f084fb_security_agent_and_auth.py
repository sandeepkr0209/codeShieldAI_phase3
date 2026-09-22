"""security agent fields (finding/observation line ranges, verification), scan warnings, users + project ownership

Revision ID: 658636f084fb
Revises: 8ede5694c63f
Create Date: 2026-09-19 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "658636f084fb"
down_revision: Union[str, None] = "8ede5694c63f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- scans: analyzer-availability warnings (Group 1) ---
    op.add_column("scans", sa.Column("warnings", sa.String(2048), nullable=True))

    # --- observations: line ranges + columns (Group 2/6) ---
    op.add_column("observations", sa.Column("start_line", sa.Integer(), nullable=True))
    op.add_column("observations", sa.Column("end_line", sa.Integer(), nullable=True))
    op.add_column("observations", sa.Column("start_column", sa.Integer(), nullable=True))
    op.add_column("observations", sa.Column("end_column", sa.Integer(), nullable=True))
    # Backfill start_line from the existing `line` column so historical
    # observations aren't left with a null start_line.
    op.execute("UPDATE observations SET start_line = line WHERE line IS NOT NULL")

    # --- findings: line ranges, analyzer provenance, verification (Group 6/12/13) ---
    op.add_column("findings", sa.Column("start_line", sa.Integer(), nullable=True))
    op.add_column("findings", sa.Column("end_line", sa.Integer(), nullable=True))
    op.add_column("findings", sa.Column("start_column", sa.Integer(), nullable=True))
    op.add_column("findings", sa.Column("end_column", sa.Integer(), nullable=True))
    op.add_column("findings", sa.Column("code_snippet", sa.Text(), nullable=True))
    op.add_column("findings", sa.Column("http_method", sa.String(10), nullable=True))
    op.add_column("findings", sa.Column("analyzer", sa.String(50), nullable=True))
    op.add_column("findings", sa.Column("rule_id", sa.String(255), nullable=True))
    op.add_column("findings", sa.Column("verified", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("findings", sa.Column("verification_method", sa.String(100), nullable=True))
    op.add_column("findings", sa.Column("verification_reason", sa.Text(), nullable=True))
    op.execute("UPDATE findings SET start_line = line WHERE line IS NOT NULL")

    # New finding_status value (potential/confirmed/open/false_positive/resolved already exist)
    op.execute("ALTER TYPE finding_status ADD VALUE IF NOT EXISTS 'accepted_risk'")

    # --- users ---
    auth_provider = postgresql.ENUM("password", "google", name="auth_provider")
    auth_provider.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("auth_provider", auth_provider, nullable=False, server_default="password"),
        sa.Column("google_id", sa.String(255), nullable=True),
        sa.Column("profile_image", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_google_id", "users", ["google_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # --- project ownership (nullable — existing projects are NOT deleted;
    #     they become "unclaimed" and remain visible to any authenticated
    #     user until claimed — see app/models/project.py) ---
    op.add_column("projects", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_projects_user_id", "projects", "users", ["user_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_user_id", "projects", type_="foreignkey")
    op.drop_column("projects", "user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_constraint("uq_users_google_id", "users", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_table("users")

    bind = op.get_bind()
    postgresql.ENUM(name="auth_provider").drop(bind, checkfirst=True)

    # Note: PostgreSQL cannot remove a value from an enum type — 'accepted_risk'
    # remains in finding_status after downgrade (documented limitation).

    op.drop_column("findings", "verification_reason")
    op.drop_column("findings", "verification_method")
    op.drop_column("findings", "verified")
    op.drop_column("findings", "rule_id")
    op.drop_column("findings", "analyzer")
    op.drop_column("findings", "http_method")
    op.drop_column("findings", "code_snippet")
    op.drop_column("findings", "end_column")
    op.drop_column("findings", "start_column")
    op.drop_column("findings", "end_line")
    op.drop_column("findings", "start_line")

    op.drop_column("observations", "end_column")
    op.drop_column("observations", "start_column")
    op.drop_column("observations", "end_line")
    op.drop_column("observations", "start_line")

    op.drop_column("scans", "warnings")
