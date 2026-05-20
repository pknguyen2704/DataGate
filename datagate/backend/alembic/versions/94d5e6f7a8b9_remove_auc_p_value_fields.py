"""remove auc p value fields

Revision ID: 94d5e6f7a8b9
Revises: 93c4d5e6f7a8
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "94d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "93c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("anomaly_results", "p_value")
    op.drop_column("model_configs", "min_history_auc_points")
    op.drop_column("model_configs", "p_value_alpha")


def downgrade() -> None:
    op.add_column(
        "model_configs",
        sa.Column("p_value_alpha", sa.Float(), nullable=False, server_default="0.05"),
    )
    op.add_column(
        "model_configs",
        sa.Column("min_history_auc_points", sa.Integer(), nullable=False, server_default="20"),
    )
    op.add_column("anomaly_results", sa.Column("p_value", sa.Float(), nullable=True))
    op.alter_column("model_configs", "p_value_alpha", server_default=None)
    op.alter_column("model_configs", "min_history_auc_points", server_default=None)
