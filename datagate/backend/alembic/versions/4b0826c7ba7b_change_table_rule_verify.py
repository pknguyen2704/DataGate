"""change table rule verify

Revision ID: 4b0826c7ba7b
Revises: c07c339c0d5c
Create Date: 2026-05-08 08:41:48.925677
"""
from typing import Sequence, Union

from alembic import op


revision: str = "4b0826c7ba7b"
down_revision: Union[str, Sequence[str], None] = "c07c339c0d5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename table, do not recreate enum/table
    op.rename_table("rule_verification_results", "rule_verify")

    # Rename indexes to match new table naming
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verification_results__rule_hour "
        "RENAME TO ix_rule_verify__rule_hour"
    )
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verification_results__rule_hour_unique "
        "RENAME TO ix_rule_verify__rule_hour_unique"
    )
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verification_results__status_hour "
        "RENAME TO ix_rule_verify__status_hour"
    )


def downgrade() -> None:
    # Rename table back
    op.rename_table("rule_verify", "rule_verification_results")

    # Rename indexes back
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verify__rule_hour "
        "RENAME TO ix_rule_verification_results__rule_hour"
    )
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verify__rule_hour_unique "
        "RENAME TO ix_rule_verification_results__rule_hour_unique"
    )
    op.execute(
        "ALTER INDEX IF EXISTS ix_rule_verify__status_hour "
        "RENAME TO ix_rule_verification_results__status_hour"
    )