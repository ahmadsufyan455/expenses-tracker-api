"""rename date to transaction_date in transactions table

Revision ID: 8e289e5af833
Revises: d250e0ccc246
Create Date: 2025-09-24 23:05:42.237411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e289e5af833'
down_revision: Union[str, Sequence[str], None] = 'd250e0ccc246'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("transactions", "date", new_column_name="transaction_date")


def downgrade() -> None:
    op.alter_column("transactions", "transaction_date", new_column_name="date")
