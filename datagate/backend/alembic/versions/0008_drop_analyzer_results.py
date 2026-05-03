"""Drop obsolete analyzer profiling storage.

Revision ID: 0008_drop_analyzer_results
Revises: 0007_add_anomaly_results
Create Date: 2026-04-28
"""

from alembic import op


revision = "0008_drop_analyzer_results"
down_revision = "0007_add_anomaly_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS analyzer_results CASCADE")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'profile_metric_name'
            ) THEN
                DROP TYPE profile_metric_name;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'profile_metric_name'
            ) THEN
                CREATE TYPE profile_metric_name AS ENUM (
                    'Completeness',
                    'Mean',
                    'StandardDeviation',
                    'Minimum',
                    'Maximum',
                    'MinLength',
                    'MaxLength',
                    'Distinctness',
                    'ApproxCountDistinct'
                );
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS analyzer_results (
            id UUID PRIMARY KEY,
            table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
            column_name VARCHAR(255) NOT NULL,
            metric_name profile_metric_name NOT NULL,
            metric_value DOUBLE PRECISION NULL,
            collected_at TIMESTAMP NOT NULL,
            CONSTRAINT uq_analyzer_results_table_column_metric
                UNIQUE (table_id, column_name, metric_name)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_analyzer_results_table_id
        ON analyzer_results (table_id)
        """
    )
