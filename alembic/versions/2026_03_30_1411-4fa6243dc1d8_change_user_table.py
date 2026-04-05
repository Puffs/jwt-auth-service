"""change user table

Revision ID: 4fa6243dc1d8
Revises: 7d8679e38396
Create Date: 2026-03-30 14:11:18.858835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fa6243dc1d8'
down_revision: Union[str, Sequence[str], None] = '7d8679e38396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role_enum = sa.Enum('USER', 'ADMIN', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    op.add_column('user', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('user', sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), server_default=sa.text("'USER'"), nullable=False))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'role')
    op.drop_column('user', 'is_active')
