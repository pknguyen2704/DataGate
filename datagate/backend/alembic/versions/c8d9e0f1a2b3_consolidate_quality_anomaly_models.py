"""consolidate quality and anomaly models

Revision ID: c8d9e0f1a2b3
Revises: b7e1c2d3f4a6
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "b7e1c2d3f4a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


severity_level = postgresql.ENUM("warning", "critical", name="severity_level")
check_status = postgresql.ENUM("pass", "fail", "error", name="check_status")
metric_scope = postgresql.ENUM(
    "metadata", "profiling", "anomaly", name="metric_scope"
)
check_type = postgresql.ENUM(
    "metadata_threshold",
    "profiling_threshold",
    "rule",
    "anomaly_auc",
    name="check_type",
)


def upgrade() -> None:
    bind = op.get_bind()
    severity_level.create(bind, checkfirst=True)
    check_status.create(bind, checkfirst=True)
    metric_scope.create(bind, checkfirst=True)
    check_type.create(bind, checkfirst=True)
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.add_column("roles", sa.Column("permissions", postgresql.JSONB(), nullable=True))
    op.execute(
        """
        UPDATE roles AS r
        SET permissions = COALESCE(p.codes, '[]'::jsonb)
        FROM (
            SELECT
                rp.role_id,
                jsonb_agg(perm.code ORDER BY perm.code) AS codes
            FROM role_permissions rp
            JOIN permissions perm ON perm.id = rp.permission_id
            GROUP BY rp.role_id
        ) p
        WHERE p.role_id = r.id
        """
    )
    op.execute("UPDATE roles SET permissions = '[]'::jsonb WHERE permissions IS NULL")
    op.execute("ALTER TABLE roles DROP CONSTRAINT IF EXISTS roles_created_by_fkey")
    op.execute("DROP INDEX IF EXISTS ix_roles__created_by")
    op.execute("ALTER TABLE roles DROP COLUMN IF EXISTS created_by")
    op.execute(
        """
        DELETE FROM roles
        WHERE name NOT IN ('Admin', 'Data Engineer', 'Data Analyst')
        """
    )
    op.execute(
        """
        INSERT INTO roles (id, name, description, permissions, is_active, is_system)
        VALUES
            (
                gen_random_uuid(),
                'Admin',
                'System-defined Admin role',
                '[
                    "user:manage",
                    "connection:view",
                    "connection:manage",
                    "table:view",
                    "table:manage",
                    "table:delete",
                    "model_config:view",
                    "model_config:update",
                    "model_config:delete",
                    "observability:view",
                    "threshold:view",
                    "threshold:manage",
                    "threshold:delete",
                    "rule:view",
                    "rule:suggest",
                    "rule:manage",
                    "quality:view",
                    "quality:resolve",
                    "home:view",
                    "lab:view"
                ]'::jsonb,
                true,
                true
            ),
            (
                gen_random_uuid(),
                'Data Engineer',
                'System-defined Data Engineer role',
                '[
                    "connection:view",
                    "table:view",
                    "table:manage",
                    "model_config:view",
                    "model_config:update",
                    "observability:view",
                    "threshold:view",
                    "threshold:manage",
                    "rule:view",
                    "rule:suggest",
                    "rule:manage",
                    "quality:view",
                    "quality:resolve",
                    "home:view",
                    "lab:view"
                ]'::jsonb,
                true,
                true
            ),
            (
                gen_random_uuid(),
                'Data Analyst',
                'System-defined Data Analyst role',
                '[
                    "table:view",
                    "model_config:view",
                    "observability:view",
                    "threshold:view",
                    "rule:view",
                    "rule:suggest",
                    "quality:view",
                    "home:view",
                    "lab:view"
                ]'::jsonb,
                true,
                true
            )
        ON CONFLICT (name) DO UPDATE
        SET
            description = COALESCE(roles.description, EXCLUDED.description),
            permissions = EXCLUDED.permissions,
            is_active = true,
            is_system = true,
            updated_at = now()
        """
    )

    op.create_table(
        "quality_metric_observations",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("metric_scope", metric_scope, nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("extra_data", postgresql.JSONB(), nullable=True),
        sa.Column("processing_date_hour", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
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

    op.create_table(
        "quality_thresholds",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("metric_scope", metric_scope, nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("min_threshold", sa.Float(), nullable=True),
        sa.Column("max_threshold", sa.Float(), nullable=True),
        sa.Column("severity_level", severity_level, nullable=False, server_default="warning"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("last_modified_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_modified_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quality_thresholds__table_scope_column_metric",
        "quality_thresholds",
        ["table_id", "metric_scope", "column_name", "metric_name"],
        unique=True,
    )
    op.create_index(
        "ix_quality_thresholds__table_active",
        "quality_thresholds",
        ["table_id", "is_active"],
    )

    op.create_table(
        "anomaly_configs",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("batch_time_col", sa.String(length=255), nullable=False),
        sa.Column("feature_config", postgresql.JSONB(), nullable=False),
        sa.Column("model_parameters", postgresql.JSONB(), nullable=False),
        sa.Column("column_config", postgresql.JSONB(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("last_modified_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_modified_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anomaly_configs__table_id", "anomaly_configs", ["table_id"], unique=True)

    op.create_table(
        "anomaly_results",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("anomaly_config_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("processing_date_hour", sa.DateTime(), nullable=False),
        sa.Column("auc_score", sa.Float(), nullable=True),
        sa.Column("p_value", sa.Float(), nullable=True),
        sa.Column("parameter_snapshot", postgresql.JSONB(), nullable=True),
        sa.Column("feature_config_snapshot", postgresql.JSONB(), nullable=True),
        sa.Column("shap_top_features", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["anomaly_config_id"], ["anomaly_configs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_anomaly_results__table_hour",
        "anomaly_results",
        ["table_id", "processing_date_hour"],
        unique=True,
    )
    op.create_index(
        "ix_anomaly_results__config_hour",
        "anomaly_results",
        ["anomaly_config_id", "processing_date_hour"],
    )

    op.create_table(
        "quality_check_results",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("table_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("check_type", check_type, nullable=False),
        sa.Column("threshold_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("rule_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("anomaly_result_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column("metric_name", sa.String(length=255), nullable=True),
        sa.Column("actual_value", sa.Float(), nullable=True),
        sa.Column("min_threshold", sa.Float(), nullable=True),
        sa.Column("max_threshold", sa.Float(), nullable=True),
        sa.Column("status", check_status, nullable=False),
        sa.Column("severity_level", severity_level, nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("resolved_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_date_hour", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["anomaly_result_id"], ["anomaly_results.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rule_id"], ["rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["threshold_id"], ["quality_thresholds.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quality_check_results__is_resolved", "quality_check_results", ["is_resolved"])
    op.create_index(
        "ix_quality_check_results__status_severity_hour",
        "quality_check_results",
        ["status", "severity_level", "processing_date_hour"],
    )
    op.create_index(
        "ix_quality_check_results__table_hour",
        "quality_check_results",
        ["table_id", "processing_date_hour"],
    )
    op.create_index(
        "ix_quality_check_results__table_type_hour",
        "quality_check_results",
        ["table_id", "check_type", "processing_date_hour"],
    )

    _migrate_data()
    _drop_old_tables()


def _migrate_data() -> None:
    op.execute(
        """
        INSERT INTO quality_metric_observations (
            id, table_id, metric_scope, column_name, metric_name, metric_value,
            extra_data, processing_date_hour, created_at, updated_at
        )
        SELECT gen_random_uuid(), m.table_id, 'metadata'::metric_scope, NULL,
               metric.metric_name, metric.metric_value,
               NULL, m.processing_date_hour, m.created_at, m.updated_at
        FROM batch_table_metadata m
        CROSS JOIN LATERAL (VALUES
            ('batch_added_rows', m.batch_added_rows::float),
            ('batch_added_files', m.batch_added_files::float),
            ('batch_added_files_size_bytes', m.batch_added_files_size_bytes::float),
            ('table_total_rows', m.table_total_rows::float),
            ('table_total_files', m.table_total_files::float),
            ('table_total_size_bytes', m.table_total_size_bytes::float)
        ) AS metric(metric_name, metric_value)
        WHERE metric.metric_value IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_metric_observations (
            id, table_id, metric_scope, column_name, metric_name, metric_value,
            extra_data, processing_date_hour, created_at, updated_at
        )
        SELECT gen_random_uuid(), p.table_id, 'profiling'::metric_scope, p.column_name,
               metric.metric_name, metric.metric_value,
               jsonb_strip_nulls(jsonb_build_object(
                   'data_type', p.data_type,
                   'min_length', p.min_length,
                   'max_length', p.max_length,
                   'approx_count_distinct', p.approx_count_distinct
               )),
               p.processing_date_hour, p.created_at, p.updated_at
        FROM batch_table_profiling p
        CROSS JOIN LATERAL (VALUES
            ('completeness', p.completeness),
            ('mean', p.mean),
            ('standard_deviation', p.standard_deviation),
            ('minimum', p.minimum),
            ('maximum', p.maximum),
            ('distinctness', p.distinctness)
        ) AS metric(metric_name, metric_value)
        WHERE metric.metric_value IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_thresholds (
            id, table_id, metric_scope, column_name, metric_name,
            min_threshold, max_threshold, severity_level, is_active, description,
            created_by, last_modified_by, created_at, updated_at
        )
        SELECT id, table_id, 'metadata'::metric_scope, NULL, metric_name,
               min_threshold, max_threshold, severity_level::text::severity_level,
               is_active, description, created_by, last_modified_by, created_at, updated_at
        FROM batch_table_metadata_manual_thresholds
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_thresholds (
            id, table_id, metric_scope, column_name, metric_name,
            min_threshold, max_threshold, severity_level, is_active, description,
            created_by, last_modified_by, created_at, updated_at
        )
        SELECT id, table_id, 'profiling'::metric_scope, column_name, metric_name,
               min_threshold, max_threshold, severity_level::text::severity_level,
               is_active, description, created_by, last_modified_by, created_at, updated_at
        FROM batch_table_profiling_manual_thresholds
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO anomaly_configs (
            id, table_id, batch_time_col, feature_config, model_parameters, column_config,
            description, created_by, last_modified_by, created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            source.table_id,
            COALESCE(mc.batch_time_col, 'processing_date_hour'),
            jsonb_build_object(
                'required_history_days', mc.required_history_days,
                'previous_batch_hours', mc.previous_batch_hours,
                'history_days', COALESCE(mc.history_days, '[]'::jsonb),
                'target_sample_per_group', mc.target_sample_per_group,
                'test_size', mc.test_size,
                'random_state', mc.random_state,
                'p_value_alpha', mc.p_value_alpha,
                'min_history_auc_points', mc.min_history_auc_points
            ),
            jsonb_build_object(
                'learning_rate', mp.learning_rate,
                'num_leaves', mp.num_leaves,
                'max_depth', mp.max_depth,
                'min_data_in_leaf', mp.min_data_in_leaf,
                'bagging_fraction', mp.bagging_fraction,
                'bagging_freq', mp.bagging_freq,
                'feature_fraction', mp.feature_fraction,
                'lambda_l1', mp.lambda_l1,
                'lambda_l2', mp.lambda_l2,
                'min_gain_to_split', mp.min_gain_to_split,
                'max_bin', mp.max_bin,
                'num_iterations', mp.num_iterations
            ),
            jsonb_build_object(
                'exclude_cols', COALESCE(mc.exclude_cols, '[]'::jsonb),
                'categorical_cols', COALESCE(mc.categorical_cols, '[]'::jsonb),
                'numeric_cols', COALESCE(mc.numeric_cols, '[]'::jsonb)
            ),
            mc.description,
            COALESCE(mc.created_by, mp.created_by),
            COALESCE(mc.last_modified_by, mp.last_modified_by),
            COALESCE(mc.created_at, mp.created_at, now()),
            COALESCE(mc.updated_at, mp.updated_at, now())
        FROM (
            SELECT table_id FROM model_configs
            UNION
            SELECT table_id FROM model_parameters
        ) source
        LEFT JOIN model_configs mc ON mc.table_id = source.table_id
        LEFT JOIN model_parameters mp ON mp.table_id = source.table_id
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_thresholds (
            id, table_id, metric_scope, column_name, metric_name,
            min_threshold, max_threshold, severity_level, is_active, description,
            created_by, last_modified_by, created_at, updated_at
        )
        SELECT amt.id, mp.table_id, 'anomaly'::metric_scope, NULL, 'auc_score',
               amt.auc_threshold, NULL, amt.severity_level::text::severity_level,
               amt.is_active, amt.description, amt.created_by, amt.last_modified_by,
               amt.created_at, amt.updated_at
        FROM auc_manual_thresholds amt
        JOIN model_parameters mp ON mp.id = amt.model_parameter_id
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO anomaly_results (
            id, table_id, anomaly_config_id, processing_date_hour, auc_score, p_value,
            parameter_snapshot, feature_config_snapshot, shap_top_features,
            created_at, updated_at
        )
        SELECT
            ar.id, ar.table_id, ac.id, ar.processing_date_hour, ar.auc_score, ar.p_value,
            ar.parameter_snapshot, ar.feature_config_snapshot,
            COALESCE(shap.features, '[]'::jsonb),
            ar.created_at, ar.updated_at
        FROM auc_results ar
        JOIN anomaly_configs ac ON ac.table_id = ar.table_id
        LEFT JOIN LATERAL (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'feature_name', s.feature_name,
                    'shap_score', s.shap_score,
                    'rank', s.shap_rank
                )
                ORDER BY s.shap_rank
            ) AS features
            FROM shap_results s
            WHERE s.auc_result_id = ar.id
        ) shap ON TRUE
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_check_results (
            id, table_id, check_type, threshold_id, column_name, metric_name,
            actual_value, min_threshold, max_threshold, status, severity_level,
            is_resolved, resolved_by, processing_date_hour, created_at, updated_at
        )
        SELECT v.id, m.table_id, 'metadata_threshold'::check_type,
               v.metadata_manual_threshold_id, NULL, t.metric_name,
               v.actual_value, v.min_threshold, v.max_threshold,
               v.status::text::check_status, v.severity_level::text::severity_level,
               v.is_resolved, v.resolved_by, v.processing_date_hour, v.created_at, v.updated_at
        FROM batch_table_metadata_metrics_verify v
        JOIN batch_table_metadata m ON m.id = v.batch_table_metadata_id
        JOIN batch_table_metadata_manual_thresholds t ON t.id = v.metadata_manual_threshold_id
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_check_results (
            id, table_id, check_type, threshold_id, column_name, metric_name,
            actual_value, min_threshold, max_threshold, status, severity_level,
            is_resolved, resolved_by, processing_date_hour, created_at, updated_at
        )
        SELECT v.id, p.table_id, 'profiling_threshold'::check_type,
               v.profiling_manual_threshold_id, p.column_name, t.metric_name,
               v.actual_value, v.min_threshold, v.max_threshold,
               v.status::text::check_status, v.severity_level::text::severity_level,
               v.is_resolved, v.resolved_by, v.processing_date_hour, v.created_at, v.updated_at
        FROM batch_table_profiling_metrics_verify v
        JOIN batch_table_profiling p ON p.id = v.batch_table_profiling_id
        JOIN batch_table_profiling_manual_thresholds t ON t.id = v.profiling_manual_threshold_id
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_check_results (
            id, table_id, check_type, rule_id, column_name, metric_name,
            status, severity_level, message, is_resolved, resolved_by,
            processing_date_hour, created_at, updated_at
        )
        SELECT v.id, r.table_id, 'rule'::check_type, v.rule_id, r.column_name,
               r.constraint_name,
               CASE
                   WHEN v.constraint_status IN ('pass', 'fail', 'error') THEN v.constraint_status
                   ELSE 'error'
               END::check_status,
               v.severity_level::text::severity_level,
               v.constraint_message, v.is_resolved, v.resolved_by,
               v.processing_date_hour, v.created_at, v.updated_at
        FROM rule_verify v
        JOIN rules r ON r.id = v.rule_id
        ON CONFLICT DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO quality_check_results (
            id, table_id, check_type, threshold_id, anomaly_result_id,
            metric_name, actual_value, min_threshold, status, severity_level,
            is_resolved, resolved_by, processing_date_hour, created_at, updated_at
        )
        SELECT v.id, ar.table_id, 'anomaly_auc'::check_type, v.manual_threshold_id,
               nr.id, 'auc_score', v.auc_score, v.auc_threshold,
               v.status::text::check_status, v.severity_level::text::severity_level,
               v.is_resolved, v.resolved_by, v.processing_date_hour, v.created_at, v.updated_at
        FROM auc_verify v
        JOIN auc_results ar ON ar.id = v.auc_result_id
        JOIN anomaly_results nr ON nr.id = ar.id
        ON CONFLICT DO NOTHING
        """
    )


def _drop_old_tables() -> None:
    for table_name in (
        "auc_verify",
        "auc_manual_thresholds",
        "shap_results",
        "auc_results",
        "model_configs",
        "model_parameters",
        "rule_verify",
        "batch_table_profiling_metrics_verify",
        "batch_table_metadata_metrics_verify",
        "batch_table_profiling_manual_thresholds",
        "batch_table_metadata_manual_thresholds",
        "batch_table_profiling",
        "batch_table_metadata",
        "role_permissions",
        "permissions",
    ):
        op.drop_table(table_name)


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade from the consolidated quality/anomaly schema is not implemented."
    )
