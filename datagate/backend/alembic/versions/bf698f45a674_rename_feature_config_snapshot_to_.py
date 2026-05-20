"""rename feature_config_snapshot to config_snapshot

Revision ID: bf698f45a674
Revises: 2d932c93f32b
Create Date: 2026-05-19 18:16:54.294793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bf698f45a674'
down_revision: Union[str, Sequence[str], None] = '2d932c93f32b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('anomaly_results', 'feature_config_snapshot', new_column_name='config_snapshot')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('anomaly_results', 'config_snapshot', new_column_name='feature_config_snapshot')
