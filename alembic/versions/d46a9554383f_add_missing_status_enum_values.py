"""add missing status enum values

Revision ID: d46a9554383f
Revises: 8cdb9622c406
Create Date: 2026-02-16 15:59:46.664786

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d46a9554383f"
down_revision: Union[str, Sequence[str], None] = "8cdb9622c406"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add all missing status values
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'IN_PROGRESS';")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'APPROVED';")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'REJECTED';")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'COMPLETED';")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'CANCELLED';")
    # -----------------------------
    # Ensure updated_at has a default now()
    # -----------------------------
    op.alter_column(
        "requests",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def downgrade():
    raise NotImplementedError("Cannot downgrade enum values safely")
