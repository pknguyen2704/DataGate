"""add lab view permission

Revision ID: 8f0b8e2a4c1d
Revises: 40d114636f41
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8f0b8e2a4c1d"
down_revision: Union[str, Sequence[str], None] = "40d114636f41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LAB_VIEW_PERMISSION_ID = "8f0b8e2a-4c1d-4a5e-9c2a-111111111111"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        f"""
        INSERT INTO permissions (id, code, name, permission_group, description)
        VALUES (
            '{LAB_VIEW_PERMISSION_ID}',
            'lab:view',
            'View Jupiter Notebook',
            'Lab',
            'Access the embedded Jupiter Notebook lab.'
        )
        ON CONFLICT (code) DO UPDATE
        SET
            name = EXCLUDED.name,
            permission_group = EXCLUDED.permission_group,
            description = EXCLUDED.description
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT roles.id, permissions.id
        FROM roles
        JOIN permissions ON permissions.code = 'lab:view'
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM role_permissions
        USING permissions
        WHERE role_permissions.permission_id = permissions.id
          AND permissions.code = 'lab:view'
        """
    )
    op.execute("DELETE FROM permissions WHERE code = 'lab:view'")
