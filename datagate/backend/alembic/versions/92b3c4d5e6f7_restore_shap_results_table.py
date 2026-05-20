"""restore shap results table

Revision ID: 92b3c4d5e6f7
Revises: 91a2b3c4d5e6
Create Date: 2026-05-18 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "92b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "91a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "anomaly_results",
        sa.Column("num_iterations_used", sa.Integer(), nullable=True),
    )
    op.create_table(
        "shap_results",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("auc_result_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("feature_name", sa.String(length=255), nullable=False),
        sa.Column("shap_score", sa.Float(), nullable=False),
        sa.Column("shap_rank", sa.Integer(), nullable=False),
        sa.Column("processing_date_hour", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["auc_result_id"], ["anomaly_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_shap_results__result_feature",
        "shap_results",
        ["auc_result_id", "feature_name"],
        unique=True,
    )
    op.execute(
        """
        INSERT INTO shap_results (
            id, auc_result_id, feature_name, shap_score, shap_rank,
            processing_date_hour, created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            ar.id,
            item ->> 'feature_name',
            (item ->> 'shap_score')::float,
            COALESCE(item ->> 'rank', item ->> 'shap_rank')::integer,
            ar.processing_date_hour,
            ar.created_at,
            ar.updated_at
        FROM anomaly_results ar
        CROSS JOIN LATERAL jsonb_array_elements(
            COALESCE(ar.shap_top_features, '[]'::jsonb)
        ) AS item
        WHERE item ->> 'feature_name' IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_shap_results__result_feature", table_name="shap_results")
    op.drop_table("shap_results")
    op.drop_column("anomaly_results", "num_iterations_used")
