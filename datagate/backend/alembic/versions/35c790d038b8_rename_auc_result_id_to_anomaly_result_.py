"""rename auc_result_id to anomaly_result_id

Revision ID: 35c790d038b8
Revises: bf698f45a674
Create Date: 2026-05-19 18:27:42.895531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35c790d038b8'
down_revision: Union[str, Sequence[str], None] = 'bf698f45a674'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('shap_results', 'auc_result_id', new_column_name='anomaly_result_id')
    op.drop_constraint('shap_results_auc_result_id_fkey', 'shap_results', type_='foreignkey')
    op.create_foreign_key('shap_results_anomaly_result_id_fkey', 'shap_results', 'anomaly_results', ['anomaly_result_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('shap_results_anomaly_result_id_fkey', 'shap_results', type_='foreignkey')
    op.alter_column('shap_results', 'anomaly_result_id', new_column_name='auc_result_id')
    op.create_foreign_key('shap_results_auc_result_id_fkey', 'shap_results', 'anomaly_results', ['auc_result_id'], ['id'], ondelete='CASCADE')
