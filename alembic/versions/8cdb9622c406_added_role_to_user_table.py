"""added_role_to_user_table

Revision ID: 8cdb9622c406
Revises: 513690a31bad
Create Date: 2026-02-03 21:03:03.753620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cdb9622c406'
down_revision: Union[str, Sequence[str], None] = '513690a31bad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    userrole_enum = sa.Enum('ADMIN', 'APPROVER', 'REQUESTER', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False, server_default='REQUESTER'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
