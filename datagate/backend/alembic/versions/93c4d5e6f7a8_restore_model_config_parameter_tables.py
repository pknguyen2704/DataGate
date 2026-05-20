"""restore model config and parameter tables

Revision ID: 93c4d5e6f7a8
Revises: 92b3c4d5e6f7
Create Date: 2026-05-18 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "93c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "92b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_configs",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("batch_time_col", sa.String(length=255), nullable=False),
        sa.Column("required_history_days", sa.Integer(), nullable=False),
        sa.Column("previous_batch_hours", sa.Integer(), nullable=False),
        sa.Column("history_days", postgresql.JSONB(), nullable=False),
        sa.Column("target_sample_per_group", sa.Integer(), nullable=False),
        sa.Column("test_size", sa.Float(), nullable=False),
        sa.Column("random_state", sa.Integer(), nullable=False),
        sa.Column("p_value_alpha", sa.Float(), nullable=False),
        sa.Column("min_history_auc_points", sa.Integer(), nullable=False),
        sa.Column("exclude_cols", postgresql.JSONB(), nullable=False),
        sa.Column("categorical_cols", postgresql.JSONB(), nullable=False),
        sa.Column("numeric_cols", postgresql.JSONB(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("last_modified_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_modified_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_model_configs__table_id", "model_configs", ["table_id"], unique=True)
    op.create_table(
        "model_parameters",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("learning_rate", sa.Float(), nullable=False),
        sa.Column("num_leaves", sa.Integer(), nullable=False),
        sa.Column("max_depth", sa.Integer(), nullable=False),
        sa.Column("min_data_in_leaf", sa.Integer(), nullable=False),
        sa.Column("bagging_fraction", sa.Float(), nullable=False),
        sa.Column("bagging_freq", sa.Integer(), nullable=False),
        sa.Column("feature_fraction", sa.Float(), nullable=False),
        sa.Column("lambda_l1", sa.Float(), nullable=False),
        sa.Column("lambda_l2", sa.Float(), nullable=False),
        sa.Column("min_gain_to_split", sa.Float(), nullable=False),
        sa.Column("max_bin", sa.Integer(), nullable=False),
        sa.Column("num_iterations", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("last_modified_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_modified_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_model_parameters__table_id", "model_parameters", ["table_id"], unique=True)
    op.execute(
        """
        INSERT INTO model_configs (
            id, table_id, batch_time_col, required_history_days, previous_batch_hours,
            history_days, target_sample_per_group, test_size, random_state,
            p_value_alpha, min_history_auc_points, exclude_cols, categorical_cols,
            numeric_cols, description, created_by, last_modified_by, created_at, updated_at
        )
        SELECT id, table_id, batch_time_col,
            (feature_config ->> 'required_history_days')::integer,
            (feature_config ->> 'previous_batch_hours')::integer,
            COALESCE(feature_config -> 'history_days', '[]'::jsonb),
            (feature_config ->> 'target_sample_per_group')::integer,
            (feature_config ->> 'test_size')::float,
            (feature_config ->> 'random_state')::integer,
            (feature_config ->> 'p_value_alpha')::float,
            (feature_config ->> 'min_history_auc_points')::integer,
            COALESCE(column_config -> 'exclude_cols', '[]'::jsonb),
            COALESCE(column_config -> 'categorical_cols', '[]'::jsonb),
            COALESCE(column_config -> 'numeric_cols', '[]'::jsonb),
            description, created_by, last_modified_by, created_at, updated_at
        FROM anomaly_configs
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO model_parameters (
            id, table_id, learning_rate, num_leaves, max_depth, min_data_in_leaf,
            bagging_fraction, bagging_freq, feature_fraction, lambda_l1, lambda_l2,
            min_gain_to_split, max_bin, num_iterations, created_by, last_modified_by,
            created_at, updated_at
        )
        SELECT gen_random_uuid(), table_id,
            (model_parameters ->> 'learning_rate')::float,
            (model_parameters ->> 'num_leaves')::integer,
            (model_parameters ->> 'max_depth')::integer,
            (model_parameters ->> 'min_data_in_leaf')::integer,
            (model_parameters ->> 'bagging_fraction')::float,
            (model_parameters ->> 'bagging_freq')::integer,
            (model_parameters ->> 'feature_fraction')::float,
            (model_parameters ->> 'lambda_l1')::float,
            (model_parameters ->> 'lambda_l2')::float,
            (model_parameters ->> 'min_gain_to_split')::float,
            (model_parameters ->> 'max_bin')::integer,
            (model_parameters ->> 'num_iterations')::integer,
            created_by, last_modified_by, created_at, updated_at
        FROM anomaly_configs
        ON CONFLICT DO NOTHING
        """
    )
    op.add_column("anomaly_results", sa.Column("model_parameter_id", sa.UUID(as_uuid=False), nullable=True))
    op.execute(
        """
        UPDATE anomaly_results ar
        SET model_parameter_id = mp.id
        FROM model_parameters mp
        WHERE mp.table_id = ar.table_id
        """
    )
    op.alter_column("anomaly_results", "model_parameter_id", nullable=False)
    op.drop_index("ix_anomaly_results__config_hour", table_name="anomaly_results")
    op.execute(
        "ALTER TABLE anomaly_results DROP CONSTRAINT IF EXISTS anomaly_results_anomaly_config_id_fkey"
    )
    op.drop_column("anomaly_results", "anomaly_config_id")
    op.create_foreign_key(
        "anomaly_results_model_parameter_id_fkey",
        "anomaly_results",
        "model_parameters",
        ["model_parameter_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_anomaly_results__param_hour",
        "anomaly_results",
        ["model_parameter_id", "processing_date_hour"],
    )
    op.drop_index("ix_anomaly_configs__table_id", table_name="anomaly_configs")
    op.drop_table("anomaly_configs")


def downgrade() -> None:
    raise NotImplementedError("Downgrade is not implemented for model config restoration.")
