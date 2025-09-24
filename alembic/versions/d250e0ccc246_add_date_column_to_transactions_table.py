"""add date column to transactions table

Revision ID: d250e0ccc246
Revises: 
Create Date: 2025-09-24 20:20:42.521632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd250e0ccc246'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add column as nullable first
    op.add_column("transactions", sa.Column("date", sa.Date(), nullable=True))

    # backfill: set date from created_att for existing records
    op.execute("UPDATE transactions SET date = DATE(created_at)")

    # then make it not nullable
    op.alter_column("transactions", "date", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("transactions", "date")
