"""user single role

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9e0f1a2b3c4"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role_id", sa.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key(
        "fk_users__role_id__roles",
        "users",
        "roles",
        ["role_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_users__role_id", "users", ["role_id"])
    op.execute(
        """
        UPDATE users u
        SET role_id = chosen.role_id
        FROM (
            SELECT DISTINCT ON (ur.user_id)
                ur.user_id,
                ur.role_id
            FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            ORDER BY
                ur.user_id,
                CASE r.name
                    WHEN 'Admin' THEN 1
                    WHEN 'Data Engineer' THEN 2
                    WHEN 'Data Analyst' THEN 3
                    ELSE 4
                END
        ) chosen
        WHERE chosen.user_id = u.id
        """
    )
    op.execute(
        """
        UPDATE users
        SET role_id = (
            SELECT id
            FROM roles
            WHERE name = 'Data Analyst'
            LIMIT 1
        )
        WHERE role_id IS NULL
        """
    )
    op.alter_column("users", "role_id", nullable=False)
    op.drop_table("user_roles")


def downgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("role_id", sa.UUID(as_uuid=False), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_index("ix_user_roles__role_id", "user_roles", ["role_id"])
    op.execute(
        """
        INSERT INTO user_roles (user_id, role_id)
        SELECT id, role_id
        FROM users
        """
    )
    op.alter_column("users", "role_id", nullable=True)
    op.drop_index("ix_users__role_id", table_name="users")
    op.drop_constraint("fk_users__role_id__roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
