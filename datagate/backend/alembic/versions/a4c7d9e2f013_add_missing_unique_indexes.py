"""add missing unique indexes

Revision ID: a4c7d9e2f013
Revises: 9b1f2d3c4a5e
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "a4c7d9e2f013"
down_revision: Union[str, Sequence[str], None] = "9b1f2d3c4a5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    return table_name in inspect(op.get_bind()).get_table_names()


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_once(index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None:
    if not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def _drop_index_once(index_name: str, table_name: str) -> None:
    if _has_index(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    """Upgrade schema."""
    _create_index_once("ix_connections__connection_name", "connections", ["connection_name"], unique=True)
    _create_index_once("ix_permissions__code", "permissions", ["code"], unique=True)
    _create_index_once("ix_roles__name", "roles", ["name"], unique=True)
    _create_index_once(
        "ix_tables__connection_catalog_schema_table",
        "tables",
        ["connection_id", "catalog_name", "schema_name", "table_name"],
        unique=True,
    )
    _create_index_once("ix_tables__connection_id", "tables", ["connection_id"])

    _create_index_once("ix_model_parameters__table_id", "model_parameters", ["table_id"], unique=True)
    _create_index_once("ix_model_configs__table_id", "model_configs", ["table_id"], unique=True)

    _create_index_once("ix_auc_results__table_hour_unique", "auc_results", ["table_id", "processing_date_hour"], unique=True)
    _create_index_once("ix_auc_verify__auc_result_id", "auc_verify", ["auc_result_id"], unique=True)
    _create_index_once("ix_shap_results__result_feature", "shap_results", ["auc_result_id", "feature_name"], unique=True)

    _create_index_once("ix_batch_table_metadata__table_hour", "batch_table_metadata", ["table_id", "processing_date_hour"], unique=True)
    _create_index_once(
        "ix_batch_table_metadata_manual_thresholds__table_metric",
        "batch_table_metadata_manual_thresholds",
        ["table_id", "metric_name"],
        unique=True,
    )
    _create_index_once(
        "ix_batch_table_metadata_metrics_verify__threshold_batch_unique",
        "batch_table_metadata_metrics_verify",
        ["metadata_manual_threshold_id", "batch_table_metadata_id"],
        unique=True,
    )

    _create_index_once(
        "ix_batch_table_profiling__table_hour_column",
        "batch_table_profiling",
        ["table_id", "processing_date_hour", "column_name"],
        unique=True,
    )
    _create_index_once(
        "ix_batch_table_profiling_manual_thresholds__table_column_metric",
        "batch_table_profiling_manual_thresholds",
        ["table_id", "column_name", "metric_name"],
        unique=True,
    )
    _create_index_once(
        "ix_batch_table_profiling_metrics_verify__threshold_batch_unique",
        "batch_table_profiling_metrics_verify",
        ["profiling_manual_threshold_id", "batch_table_profiling_id"],
        unique=True,
    )

    _create_index_once("ix_rule_verify__rule_hour_unique", "rule_verify", ["rule_id", "processing_date_hour"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    _drop_index_once("ix_rule_verify__rule_hour_unique", "rule_verify")
    _drop_index_once("ix_batch_table_profiling_metrics_verify__threshold_batch_unique", "batch_table_profiling_metrics_verify")
    _drop_index_once("ix_batch_table_profiling_manual_thresholds__table_column_metric", "batch_table_profiling_manual_thresholds")
    _drop_index_once("ix_batch_table_profiling__table_hour_column", "batch_table_profiling")
    _drop_index_once("ix_batch_table_metadata_metrics_verify__threshold_batch_unique", "batch_table_metadata_metrics_verify")
    _drop_index_once("ix_batch_table_metadata_manual_thresholds__table_metric", "batch_table_metadata_manual_thresholds")
    _drop_index_once("ix_batch_table_metadata__table_hour", "batch_table_metadata")
    _drop_index_once("ix_shap_results__result_feature", "shap_results")
    _drop_index_once("ix_auc_verify__auc_result_id", "auc_verify")
    _drop_index_once("ix_auc_results__table_hour_unique", "auc_results")
    _drop_index_once("ix_model_configs__table_id", "model_configs")
    _drop_index_once("ix_model_parameters__table_id", "model_parameters")
    _drop_index_once("ix_tables__connection_id", "tables")
    _drop_index_once("ix_tables__connection_catalog_schema_table", "tables")
    _drop_index_once("ix_roles__name", "roles")
    _drop_index_once("ix_permissions__code", "permissions")
    _drop_index_once("ix_connections__connection_name", "connections")
