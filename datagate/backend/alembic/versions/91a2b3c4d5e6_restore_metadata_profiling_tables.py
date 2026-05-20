"""restore metadata and profiling metric tables

Revision ID: 91a2b3c4d5e6
Revises: 90f1a2b3c4d6
Create Date: 2026-05-18 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "91a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "90f1a2b3c4d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batch_table_metadata",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("batch_added_rows", sa.BigInteger(), nullable=True),
        sa.Column("batch_added_files", sa.Integer(), nullable=True),
        sa.Column("batch_added_files_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("table_total_rows", sa.BigInteger(), nullable=True),
        sa.Column("table_total_files", sa.Integer(), nullable=True),
        sa.Column("table_total_size_bytes", sa.BigInteger(), nullable=True),
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
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_batch_table_metadata__table_hour",
        "batch_table_metadata",
        ["table_id", "processing_date_hour"],
        unique=True,
    )
    op.create_index(
        "ix_batch_table_metadata__processing_date_hour",
        "batch_table_metadata",
        ["processing_date_hour"],
    )

    op.create_table(
        "batch_table_profiling",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=False),
        sa.Column("data_type", sa.String(length=100), nullable=True),
        sa.Column("completeness", sa.Float(), nullable=True),
        sa.Column("mean", sa.Float(), nullable=True),
        sa.Column("standard_deviation", sa.Float(), nullable=True),
        sa.Column("minimum", sa.Float(), nullable=True),
        sa.Column("maximum", sa.Float(), nullable=True),
        sa.Column("min_length", sa.Integer(), nullable=True),
        sa.Column("max_length", sa.Integer(), nullable=True),
        sa.Column("distinctness", sa.Float(), nullable=True),
        sa.Column("approx_count_distinct", sa.BigInteger(), nullable=True),
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
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_batch_table_profiling__table_hour_column",
        "batch_table_profiling",
        ["table_id", "processing_date_hour", "column_name"],
        unique=True,
    )
    op.create_index(
        "ix_batch_table_profiling__table_column_hour",
        "batch_table_profiling",
        ["table_id", "column_name", "processing_date_hour"],
    )
    op.create_index(
        "ix_batch_table_profiling__processing_date_hour",
        "batch_table_profiling",
        ["processing_date_hour"],
    )

    op.execute(
        """
        INSERT INTO batch_table_metadata (
            id, table_id, batch_added_rows, batch_added_files,
            batch_added_files_size_bytes, table_total_rows, table_total_files,
            table_total_size_bytes, processing_date_hour, created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            table_id,
            MAX(metric_value) FILTER (WHERE metric_name = 'batch_added_rows')::bigint,
            MAX(metric_value) FILTER (WHERE metric_name = 'batch_added_files')::integer,
            MAX(metric_value) FILTER (WHERE metric_name = 'batch_added_files_size_bytes')::bigint,
            MAX(metric_value) FILTER (WHERE metric_name = 'table_total_rows')::bigint,
            MAX(metric_value) FILTER (WHERE metric_name = 'table_total_files')::integer,
            MAX(metric_value) FILTER (WHERE metric_name = 'table_total_size_bytes')::bigint,
            processing_date_hour,
            MIN(created_at),
            MAX(updated_at)
        FROM quality_metric_observations
        WHERE metric_scope = 'metadata'
        GROUP BY table_id, processing_date_hour
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO batch_table_profiling (
            id, table_id, column_name, data_type, completeness, mean,
            standard_deviation, minimum, maximum, min_length, max_length,
            distinctness, approx_count_distinct, processing_date_hour,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            table_id,
            column_name,
            MAX(extra_data ->> 'data_type'),
            MAX(metric_value) FILTER (WHERE metric_name = 'completeness'),
            MAX(metric_value) FILTER (WHERE metric_name = 'mean'),
            MAX(metric_value) FILTER (WHERE metric_name = 'standard_deviation'),
            MAX(metric_value) FILTER (WHERE metric_name = 'minimum'),
            MAX(metric_value) FILTER (WHERE metric_name = 'maximum'),
            COALESCE(
                MAX(metric_value) FILTER (WHERE metric_name = 'min_length'),
                MAX((extra_data ->> 'min_length')::float)
            )::integer,
            COALESCE(
                MAX(metric_value) FILTER (WHERE metric_name = 'max_length'),
                MAX((extra_data ->> 'max_length')::float)
            )::integer,
            MAX(metric_value) FILTER (WHERE metric_name = 'distinctness'),
            COALESCE(
                MAX(metric_value) FILTER (WHERE metric_name = 'approx_count_distinct'),
                MAX((extra_data ->> 'approx_count_distinct')::float)
            )::bigint,
            processing_date_hour,
            MIN(created_at),
            MAX(updated_at)
        FROM quality_metric_observations
        WHERE metric_scope = 'profiling'
          AND column_name IS NOT NULL
        GROUP BY table_id, column_name, processing_date_hour
        ON CONFLICT DO NOTHING
        """
    )

    op.drop_index(
        "ix_quality_metric_observations__table_scope_metric",
        table_name="quality_metric_observations",
    )
    op.drop_index(
        "ix_quality_metric_observations__table_hour",
        table_name="quality_metric_observations",
    )
    op.drop_index(
        "ix_quality_metric_observations__table_hour_scope_column_metric",
        table_name="quality_metric_observations",
    )
    op.drop_table("quality_metric_observations")


def downgrade() -> None:
    op.create_table(
        "quality_metric_observations",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("metric_scope", sa.String(length=50), nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("extra_data", postgresql.JSONB(), nullable=True),
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
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_metric_observations__table_hour_scope_column_metric",
        "quality_metric_observations",
        ["table_id", "processing_date_hour", "metric_scope", "column_name", "metric_name"],
        unique=True,
    )
    op.create_index(
        "ix_quality_metric_observations__table_hour",
        "quality_metric_observations",
        ["table_id", "processing_date_hour"],
    )
    op.create_index(
        "ix_quality_metric_observations__table_scope_metric",
        "quality_metric_observations",
        ["table_id", "metric_scope", "metric_name"],
    )

    op.drop_index("ix_batch_table_profiling__processing_date_hour", table_name="batch_table_profiling")
    op.drop_index("ix_batch_table_profiling__table_column_hour", table_name="batch_table_profiling")
    op.drop_index("ix_batch_table_profiling__table_hour_column", table_name="batch_table_profiling")
    op.drop_table("batch_table_profiling")
    op.drop_index("ix_batch_table_metadata__processing_date_hour", table_name="batch_table_metadata")
    op.drop_index("ix_batch_table_metadata__table_hour", table_name="batch_table_metadata")
    op.drop_table("batch_table_metadata")
