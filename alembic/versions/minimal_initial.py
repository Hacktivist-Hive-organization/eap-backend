"""minimal_initial_setup

Revision ID: min_setup
Revises:
Create Date: 2026-03-08 12:00:00

"""

import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "min_setup"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, unique=True, nullable=False, index=True),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "APPROVER", "REQUESTER", name="userrole"),
            nullable=False,
            server_default="REQUESTER",
        ),
        sa.Column(
            "is_email_verified", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "is_out_of_office", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    # --- request_types ---
    op.create_table(
        "request_types",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
    )

    # --- request_subtypes ---
    op.create_table(
        "request_subtypes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "type_id", sa.Integer, sa.ForeignKey("request_types.id"), nullable=False
        ),
    )

    # --- requests ---
    op.create_table(
        "requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "type_id", sa.Integer, sa.ForeignKey("request_types.id"), nullable=False
        ),
        sa.Column(
            "subtype_id",
            sa.Integer,
            sa.ForeignKey("request_subtypes.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("business_justification", sa.String(1000), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", name="priority"),
            nullable=False,
        ),
        sa.Column(
            "current_status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "IN_PROGRESS",
                "APPROVED",
                "REJECTED",
                "COMPLETED",
                "CANCELLED",
                name="status",
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
        sa.Column(
            "requester_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False
        ),
    )
    op.create_index(
        "ix_requests_dashboard",
        "requests",
        ["requester_id", "current_status", "updated_at"],
    )

    # --- request_tracking ---
    op.create_table(
        "request_tracking",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("comment", sa.String(2000)),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "IN_PROGRESS",
                "APPROVED",
                "REJECTED",
                "COMPLETED",
                "CANCELLED",
                name="status",
            ),
            nullable=False,
            server_default="SUBMITTED",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "request_id", sa.Integer, sa.ForeignKey("requests.id"), nullable=False
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    )

    # --- request_type_approvers ---
    op.create_table(
        "request_type_approvers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "request_type_id",
            sa.Integer,
            sa.ForeignKey("request_types.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("workload", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("request_type_id", "user_id", name="uq_request_type_user"),
    )


def downgrade():
    op.drop_table("request_type_approvers")
    op.drop_table("request_tracking")
    op.drop_index("ix_requests_dashboard", table_name="requests")
    op.drop_table("requests")
    op.drop_table("request_subtypes")
    op.drop_table("request_types")
    op.drop_table("users")
