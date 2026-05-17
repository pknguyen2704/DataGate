"""rename auc scores to auc results

Revision ID: 9b1f2d3c4a5e
Revises: 61d08c3f61de
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "9b1f2d3c4a5e"
down_revision: Union[str, Sequence[str], None] = "61d08c3f61de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    return table_name in inspect(op.get_bind()).get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_once(index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None:
    if _has_table(table_name) and not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def _drop_index_once(index_name: str, table_name: str) -> None:
    if _has_index(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    """Upgrade schema."""
    if _has_table("auc_scores") and not _has_table("auc_results"):
        _drop_index_once("ix_auc_scores__param_hour", "auc_scores")
        _drop_index_once("ix_auc_scores__table_hour", "auc_scores")
        op.rename_table("auc_scores", "auc_results")

    _create_index_once("ix_auc_results__param_hour", "auc_results", ["model_parameter_id", "processing_date_hour"])
    _create_index_once("ix_auc_results__table_hour", "auc_results", ["table_id", "processing_date_hour"])

    if _has_table("auc_verify") and not _has_column("auc_verify", "auc_score"):
        op.add_column("auc_verify", sa.Column("auc_score", sa.Float(), nullable=True))

    _create_index_once("ix_auc_verify__auc_result_id", "auc_verify", ["auc_result_id"], unique=True)
    _create_index_once("ix_model_configs__table_id", "model_configs", ["table_id"], unique=True)
    _create_index_once("ix_model_parameters__table_id", "model_parameters", ["table_id"], unique=True)
    _create_index_once("ix_shap_results__auc_result_rank", "shap_results", ["auc_result_id", "shap_rank"])


def downgrade() -> None:
    """Downgrade schema."""
    _drop_index_once("ix_shap_results__auc_result_rank", "shap_results")
    _drop_index_once("ix_model_parameters__table_id", "model_parameters")
    _drop_index_once("ix_model_configs__table_id", "model_configs")
    _drop_index_once("ix_auc_verify__auc_result_id", "auc_verify")

    if _has_column("auc_verify", "auc_score"):
        op.drop_column("auc_verify", "auc_score")

    _drop_index_once("ix_auc_results__table_hour", "auc_results")
    _drop_index_once("ix_auc_results__param_hour", "auc_results")

    if _has_table("auc_results") and not _has_table("auc_scores"):
        op.rename_table("auc_results", "auc_scores")
        _create_index_once("ix_auc_scores__param_hour", "auc_scores", ["model_parameter_id", "processing_date_hour"])
        _create_index_once("ix_auc_scores__table_hour", "auc_scores", ["table_id", "processing_date_hour"])
