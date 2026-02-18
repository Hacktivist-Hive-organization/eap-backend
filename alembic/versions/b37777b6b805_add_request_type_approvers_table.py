"""add request_type_approvers table

Revision ID: b37777b6b805
Revises: 626fe01567d4
Create Date: 2026-02-18 12:11:23.508876

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b37777b6b805"
down_revision: Union[str, Sequence[str], None] = "626fe01567d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "request_type_approvers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_type_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("workload", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["request_type_id"], ["request_types.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_type_id", "user_id", name="uq_request_type_user"),
    )

    # Add indexes for better performance
    op.create_index(
        "ix_request_type_approvers_request_type_id",
        "request_type_approvers",
        ["request_type_id"],
    )
    op.create_index(
        "ix_request_type_approvers_user_id", "request_type_approvers", ["user_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes first
    op.drop_index(
        "ix_request_type_approvers_user_id", table_name="request_type_approvers"
    )
    op.drop_index(
        "ix_request_type_approvers_request_type_id", table_name="request_type_approvers"
    )

    # Drop the table
    op.drop_table("request_type_approvers")
