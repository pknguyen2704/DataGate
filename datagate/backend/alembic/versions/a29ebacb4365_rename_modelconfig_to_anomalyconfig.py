"""Rename ModelConfig to AnomalyConfig

Revision ID: a29ebacb4365
Revises: bf3f5207ab62
Create Date: 2026-05-22 08:52:36.934853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a29ebacb4365'
down_revision: Union[str, Sequence[str], None] = 'bf3f5207ab62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('model_configs', 'anomaly_configs')
    op.execute('ALTER INDEX ix_model_configs__table_id RENAME TO ix_anomaly_configs__table_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('anomaly_configs', 'model_configs')
    op.execute('ALTER INDEX ix_anomaly_configs__table_id RENAME TO ix_model_configs__table_id')
    # ### end Alembic commands ###
