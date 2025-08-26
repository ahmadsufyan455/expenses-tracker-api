"""Add unique constraint to budgets table

Revision ID: c5e7d0cfd0bd
Revises: e801326ace47
Create Date: 2025-08-26 21:57:29.462576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5e7d0cfd0bd'
down_revision: Union[str, None] = 'e801326ace47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_user_category_month",
        "budgets",
        ["user_id", "category_id", "month"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_category_month", "budgets", type_="unique")
