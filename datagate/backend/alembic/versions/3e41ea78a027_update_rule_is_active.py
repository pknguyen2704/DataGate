"""update rule is active

Revision ID: 3e41ea78a027
Revises: a7623ea11ed7
Create Date: 2026-05-13 10:30:46.406596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '3e41ea78a027'
down_revision: Union[str, Sequence[str], None] = 'a7623ea11ed7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new column as nullable first
    op.add_column(
        'rules',
        sa.Column('is_active', sa.Boolean(), nullable=True)
    )

    # 2. Migrate old status data to is_active
    # active   -> true
    # inactive -> false
    # pending  -> false
    op.execute("""
        UPDATE rules
        SET is_active = CASE
            WHEN status = 'active' THEN true
            ELSE false
        END
    """)

    # 3. Now safe to set NOT NULL
    op.alter_column(
        'rules',
        'is_active',
        existing_type=sa.Boolean(),
        nullable=False
    )

    # 4. Drop old indexes using status
    op.drop_index(op.f('ix_rules__table_source_status'), table_name='rules')
    op.drop_index(op.f('ix_rules__table_status'), table_name='rules')

    # 5. Drop old status column
    op.drop_column('rules', 'status')

    # 6. Create new indexes using is_active
    op.create_index(
        'ix_rules__table_source_is_active',
        'rules',
        ['table_id', 'source', 'is_active'],
        unique=False
    )

    op.create_index(
        'ix_rules__table_is_active',
        'rules',
        ['table_id', 'is_active'],
        unique=False
    )


def downgrade() -> None:
    rule_status_enum = postgresql.ENUM(
        'pending',
        'active',
        'inactive',
        name='rule_status'
    )

    # Make sure enum type exists
    rule_status_enum.create(op.get_bind(), checkfirst=True)

    # 1. Add status back as nullable first
    op.add_column(
        'rules',
        sa.Column('status', rule_status_enum, nullable=True)
    )

    # 2. Migrate is_active back to status
    # Note: old pending status cannot be recovered
    op.execute("""
        UPDATE rules
        SET status = CASE
            WHEN is_active = true THEN 'active'::rule_status
            ELSE 'inactive'::rule_status
        END
    """)

    # 3. Set status NOT NULL
    op.alter_column(
        'rules',
        'status',
        existing_type=rule_status_enum,
        nullable=False
    )

    # 4. Drop new indexes
    op.drop_index('ix_rules__table_source_is_active', table_name='rules')
    op.drop_index('ix_rules__table_is_active', table_name='rules')

    # 5. Drop is_active
    op.drop_column('rules', 'is_active')

    # 6. Recreate old indexes
    op.create_index(
        op.f('ix_rules__table_source_status'),
        'rules',
        ['table_id', 'source', 'status'],
        unique=False
    )

    op.create_index(
        op.f('ix_rules__table_status'),
        'rules',
        ['table_id', 'status'],
        unique=False
    )