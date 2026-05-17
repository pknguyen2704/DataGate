"""add missing user unique indexes

Revision ID: b7e1c2d3f4a6
Revises: a4c7d9e2f013
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "b7e1c2d3f4a6"
down_revision: Union[str, Sequence[str], None] = "a4c7d9e2f013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_index(table_name: str, index_name: str) -> bool:
    return index_name in {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    """Upgrade schema."""
    if not _has_index("users", "ix_users__email"):
        op.create_index("ix_users__email", "users", ["email"], unique=True)
    if not _has_index("users", "ix_users__username"):
        op.create_index("ix_users__username", "users", ["username"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    if _has_index("users", "ix_users__username"):
        op.drop_index("ix_users__username", table_name="users")
    if _has_index("users", "ix_users__email"):
        op.drop_index("ix_users__email", table_name="users")
