"""Add persisted anomaly detection results.

Revision ID: 0007_add_anomaly_results
Revises: 0006_reconcile_current
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0007_add_anomaly_results"
down_revision = "0006_reconcile_current"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "anomaly_results",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column(
            "table_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date_column", sa.String(length=255), nullable=False),
        sa.Column("batch_date_hour", sa.String(length=30), nullable=False),
        sa.Column("target_date", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("auc", sa.Float(), nullable=True),
        sa.Column("sample_today_count", sa.Integer(), nullable=True),
        sa.Column("sample_comparison_count", sa.Integer(), nullable=True),
        sa.Column("sample_total_count", sa.Integer(), nullable=True),
        sa.Column("anomaly_count", sa.Integer(), nullable=True),
        sa.Column("severity_counts", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("root_causes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("examples", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "table_id",
            "date_column",
            "batch_date_hour",
            name="uq_anomaly_results_table_date_column_batch",
        ),
    )
    op.create_index("ix_anomaly_results_table_id", "anomaly_results", ["table_id"])
    op.create_index(
        "ix_anomaly_results_table_target_date",
        "anomaly_results",
        ["table_id", "target_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_anomaly_results_table_target_date", table_name="anomaly_results")
    op.drop_index("ix_anomaly_results_table_id", table_name="anomaly_results")
    op.drop_table("anomaly_results")
