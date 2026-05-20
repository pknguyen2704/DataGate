"""remove p value generated auc checks

Revision ID: 95e6f7a8b9c0
Revises: 94d5e6f7a8b9
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "95e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "94d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM quality_check_results
        WHERE check_type = 'anomaly_auc'
          AND threshold_id IS NULL
        """
    )


def downgrade() -> None:
    pass
