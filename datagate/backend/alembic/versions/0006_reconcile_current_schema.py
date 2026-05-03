"""Reconcile current schema after feature removals and rule upsert drift.

Revision ID: 0006_reconcile_current
Revises: 0005_drop_table_description
Create Date: 2026-04-28
"""

from alembic import op


revision = "0006_reconcile_current"
down_revision = "0005_drop_table_description"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS schema_change_events CASCADE")
    op.execute("DROP TABLE IF EXISTS table_schema_change_events CASCADE")
    op.execute("DROP TABLE IF EXISTS table_schema_metadata CASCADE")
    op.execute("ALTER TABLE tables DROP COLUMN IF EXISTS description")

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

    op.execute(
        """
        DELETE FROM rules r
        USING (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY table_id, source, rule_signature
                        ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST, id DESC
                    ) AS row_number
                FROM rules
                WHERE rule_signature IS NOT NULL
            ) ranked
            WHERE ranked.row_number > 1
        ) duplicates
        WHERE r.id = duplicates.id
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_rules_table_source_signature
        ON rules (table_id, source, rule_signature)
        WHERE rule_signature IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_rules_table_source_signature")
    op.execute("ALTER TABLE tables ADD COLUMN IF NOT EXISTS description TEXT")
