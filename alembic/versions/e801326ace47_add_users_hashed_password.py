"""add users.hashed_password

Revision ID: e801326ace47
Revises: 
Create Date: 2025-08-23 12:28:46.679807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e801326ace47'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String()))


def downgrade() -> None:
    pass
