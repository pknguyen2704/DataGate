"""make quality check severity not null

Revision ID: 90f1a2b3c4d6
Revises: 477b2bcfc34d
Create Date: 2026-05-18 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90f1a2b3c4d6"
down_revision: Union[str, Sequence[str], None] = "477b2bcfc34d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE quality_check_results SET severity_level = 'warning' WHERE severity_level IS NULL"
    )
    op.alter_column(
        "quality_check_results",
        "severity_level",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "quality_check_results",
        "severity_level",
        existing_type=sa.String(length=50),
        nullable=True,
    )
