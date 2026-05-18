from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Role
from app.rbac.roles import DEFAULT_ROLE_PERMISSIONS


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def list_roles(self, page: int = 1, page_size: int = 50) -> dict:
        query = self.db.query(Role).filter(
            Role.name.in_(DEFAULT_ROLE_PERMISSIONS.keys()),
        )

        total = query.count()
        items = (
            query.order_by(Role.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_role_by_id(self, role_id: str) -> Role | None:
        return (
            self.db.query(Role)
            .filter(
                Role.id == role_id,
                Role.name.in_(DEFAULT_ROLE_PERMISSIONS.keys()),
            )
            .first()
        )

    def get_role_or_404(self, role_id: str) -> Role:
        role = self.get_role_by_id(role_id)

        if role is None:
            raise NotFoundError("Role not found")

        return role

    def get_role_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()
