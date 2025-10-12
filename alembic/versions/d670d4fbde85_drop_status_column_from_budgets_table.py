"""drop status column from budgets table

Revision ID: d670d4fbde85
Revises: 8e289e5af833
Create Date: 2025-10-12 13:54:54.762280

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d670d4fbde85"
down_revision: Union[str, Sequence[str], None] = "8e289e5af833"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("budgets", "status")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("budgets", sa.Column("status", sa.INTEGER(), autoincrement=False, nullable=False))
