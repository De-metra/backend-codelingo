"""make last_activity nullable

Revision ID: 12cb0ad6f8dc
Revises: d9a501cd747b
Create Date: 2026-01-04 18:09:31.345539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12cb0ad6f8dc'
down_revision: Union[str, Sequence[str], None] = 'd9a501cd747b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users_stats",
        "last_activity",
        existing_type=sa.DateTime(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users_stats",
        "last_activity",
        existing_type=sa.DateTime(),
        nullable=False,
    )
