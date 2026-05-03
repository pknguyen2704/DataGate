"""Add rule frequency fields and verification results.

Revision ID: 0003_rule_verify
Revises: 0002_schema_metadata_jsonb
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_rule_verify"
down_revision = "0002_schema_metadata_jsonb"
branch_labels = None
depends_on = None


rule_verification_status = postgresql.ENUM(
    "passed",
    "failed",
    "error",
    name="rule_verification_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'rule_verification_status'
            ) THEN
                CREATE TYPE rule_verification_status AS ENUM ('passed', 'failed', 'error');
            END IF;
        END
        $$;
        """
    )

    op.execute("ALTER TABLE rules ADD COLUMN IF NOT EXISTS rule_signature VARCHAR(64)")
    op.execute("ALTER TABLE rules ADD COLUMN IF NOT EXISTS frequency INTEGER")
    op.execute("ALTER TABLE rules ADD COLUMN IF NOT EXISTS first_seen_at_date_hour VARCHAR(30)")
    op.execute("ALTER TABLE rules ADD COLUMN IF NOT EXISTS last_seen_at_date_hour VARCHAR(30)")

    op.execute("UPDATE rules SET frequency = 1 WHERE frequency IS NULL")
    op.execute("ALTER TABLE rules ALTER COLUMN frequency SET NOT NULL")
    op.execute("ALTER TABLE rules ALTER COLUMN frequency SET DEFAULT 1")

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rules_table_signature ON rules (table_id, rule_signature)"
    )

    op.execute(
        """
        UPDATE rules
        SET
            frequency = COALESCE(frequency, 1),
            first_seen_at_date_hour = COALESCE(first_seen_at_date_hour, suggested_at_date_hour),
            last_seen_at_date_hour = COALESCE(last_seen_at_date_hour, suggested_at_date_hour),
            rule_signature = COALESCE(rule_signature, md5(
                coalesce(table_id::text, '') || '|' ||
                coalesce(column_name, '') || '|' ||
                coalesce(constraint_type::text, '') || '|' ||
                coalesce(value_set, '') || '|' ||
                coalesce(regex_pattern, '') || '|' ||
                coalesce(threshold_min::text, '') || '|' ||
                coalesce(threshold_max::text, '')
            ))
        WHERE source = 'system'
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

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS rule_verification_results (
            id UUID PRIMARY KEY,
            rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
            table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
            batch_date_hour VARCHAR(30) NOT NULL,
            verification_status rule_verification_status NOT NULL,
            actual_value VARCHAR(255),
            expected_value VARCHAR(255),
            failure_count INTEGER,
            total_count INTEGER,
            message TEXT,
            verified_at TIMESTAMP NOT NULL,
            CONSTRAINT uq_rule_verification_rule_batch UNIQUE (rule_id, batch_date_hour)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rule_verification_results_rule_id ON rule_verification_results (rule_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rule_verification_results_table_id ON rule_verification_results (table_id)"
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_rule_verification_table_batch
        ON rule_verification_results (table_id, batch_date_hour)
        """
    )

    op.execute("ALTER TABLE rules ALTER COLUMN frequency DROP DEFAULT")


def downgrade() -> None:
    op.drop_index("ix_rule_verification_table_batch", table_name="rule_verification_results")
    op.drop_index("ix_rule_verification_results_table_id", table_name="rule_verification_results")
    op.drop_index("ix_rule_verification_results_rule_id", table_name="rule_verification_results")
    op.drop_table("rule_verification_results")

    op.drop_index("ix_rules_table_signature", table_name="rules")
    op.drop_index("uq_rules_table_source_signature", table_name="rules")
    op.drop_column("rules", "last_seen_at_date_hour")
    op.drop_column("rules", "first_seen_at_date_hour")
    op.drop_column("rules", "frequency")
    op.drop_column("rules", "rule_signature")

    op.execute("DROP TYPE IF EXISTS rule_verification_status")
