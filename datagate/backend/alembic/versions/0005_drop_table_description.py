"""Drop description column from tables.

Revision ID: 0005_drop_table_description
Revises: 0004_drop_unused_schema
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_drop_table_description"
down_revision = "0004_drop_unused_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE tables DROP COLUMN IF EXISTS description")


def downgrade() -> None:
    op.execute("ALTER TABLE tables ADD COLUMN IF NOT EXISTS description TEXT")
