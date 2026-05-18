"""remove user table role active flags

Revision ID: e0f1a2b3c4d5
Revises: d9e0f1a2b3c4
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e0f1a2b3c4d5"
down_revision: Union[str, Sequence[str], None] = "d9e0f1a2b3c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_users__is_active", table_name="users")
    op.drop_column("users", "is_active")

    op.drop_index("ix_roles__is_active", table_name="roles")
    op.drop_index("ix_roles__is_system", table_name="roles")
    op.drop_column("roles", "is_active")
    op.drop_column("roles", "is_system")

    op.drop_index("ix_tables__is_active", table_name="tables")
    op.drop_column("tables", "is_active")

    op.execute("ALTER TABLE tables DROP CONSTRAINT IF EXISTS tables_connection_id_fkey")
    op.execute("ALTER TABLE tables DROP CONSTRAINT IF EXISTS fk_tables__connection_id__connections")
    op.create_foreign_key(
        "fk_tables__connection_id__connections",
        "tables",
        "connections",
        ["connection_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        "ALTER TABLE anomaly_results DROP CONSTRAINT IF EXISTS anomaly_results_anomaly_config_id_fkey"
    )
    op.execute(
        "ALTER TABLE anomaly_results DROP CONSTRAINT IF EXISTS fk_anomaly_results__anomaly_config_id__anomaly_configs"
    )
    op.create_foreign_key(
        "fk_anomaly_results__anomaly_config_id__anomaly_configs",
        "anomaly_results",
        "anomaly_configs",
        ["anomaly_config_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE anomaly_results DROP CONSTRAINT IF EXISTS fk_anomaly_results__anomaly_config_id__anomaly_configs"
    )
    op.create_foreign_key(
        "anomaly_results_anomaly_config_id_fkey",
        "anomaly_results",
        "anomaly_configs",
        ["anomaly_config_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.execute("ALTER TABLE tables DROP CONSTRAINT IF EXISTS fk_tables__connection_id__connections")
    op.create_foreign_key(
        "tables_connection_id_fkey",
        "tables",
        "connections",
        ["connection_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.add_column(
        "tables",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_tables__is_active", "tables", ["is_active"])

    op.add_column(
        "roles",
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "roles",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_roles__is_system", "roles", ["is_system"])
    op.create_index("ix_roles__is_active", "roles", ["is_active"])

    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_users__is_active", "users", ["is_active"])
