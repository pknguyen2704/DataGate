"""Drop unused schema tracking tables.

Revision ID: 0004_drop_unused_schema
Revises: 0003_rule_verify
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_drop_unused_schema"
down_revision = "0003_rule_verify"
branch_labels = None
depends_on = None


schema_change_type = postgresql.ENUM(
    "added",
    "removed",
    "type_changed",
    name="schema_change_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS schema_change_events CASCADE")
    op.execute("DROP TABLE IF EXISTS table_schema_change_events CASCADE")
    op.execute("DROP TABLE IF EXISTS table_schema_metadata CASCADE")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'schema_change_type'
            ) THEN
                DROP TYPE schema_change_type;
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
                SELECT 1 FROM pg_type WHERE typname = 'schema_change_type'
            ) THEN
                CREATE TYPE schema_change_type AS ENUM ('added', 'removed', 'type_changed');
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "table_schema_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column(
            "table_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("catalog_name", sa.String(length=255), nullable=True),
        sa.Column("schema_name", sa.String(length=255), nullable=True),
        sa.Column("table_name", sa.String(length=255), nullable=True),
        sa.Column("snapshot_id", sa.String(length=255), nullable=False),
        sa.Column("schema_id", sa.Integer(), nullable=True),
        sa.Column("columns", postgresql.JSONB(), nullable=False),
        sa.Column("collected_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "table_id",
            "snapshot_id",
            name="uq_table_schema_metadata_table_snapshot",
        ),
    )
    op.create_index(
        "ix_table_schema_metadata_table_id",
        "table_schema_metadata",
        ["table_id"],
    )
    op.create_index(
        "ix_table_schema_metadata_snapshot_id",
        "table_schema_metadata",
        ["snapshot_id"],
    )
    op.create_index(
        "ix_table_schema_metadata_columns_gin",
        "table_schema_metadata",
        ["columns"],
        postgresql_using="gin",
    )

    op.create_table(
        "schema_change_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column(
            "table_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("snapshot_id", sa.String(length=255), nullable=True),
        sa.Column("change_type", schema_change_type, nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=False),
        sa.Column("old_type", sa.String(length=100), nullable=True),
        sa.Column("new_type", sa.String(length=100), nullable=True),
        sa.Column(
            "detected_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_schema_change_events_table_id", "schema_change_events", ["table_id"])
    op.create_index("ix_schema_change_events_snapshot_id", "schema_change_events", ["snapshot_id"])
    op.create_index(
        "ix_schema_change_events_table_detected_at",
        "schema_change_events",
        ["table_id", "detected_at"],
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_rules_table_source_signature
        ON rules (table_id, source, rule_signature)
        WHERE rule_signature IS NOT NULL
        """
    )
