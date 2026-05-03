from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError, BadRequestError
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def list_permissions(self) -> list[Permission]:
        return (
            self.db.query(Permission)
            .order_by(Permission.group.asc(), Permission.name.asc())
            .all()
        )

    def list_roles(self) -> list[Role]:
        return (
            self.db.query(Role)
            .options(selectinload(Role.permissions))
            .order_by(Role.created_at.desc())
            .all()
        )

    def get_role_by_id(self, role_id: str) -> Role | None:
        return (
            self.db.query(Role)
            .options(selectinload(Role.permissions))
            .filter(Role.id == role_id)
            .first()
        )

    def get_role_or_404(self, role_id: str) -> Role:
        role = self.get_role_by_id(role_id)

        if role is None:
            raise NotFoundError("Role not found")

        return role

    def get_role_by_name(self, name: str) -> Role | None:
        return (
            self.db.query(Role)
            .filter(Role.name == name)
            .first()
        )

    def create_role(self, data: RoleCreate) -> Role:
        existing_role = self.get_role_by_name(data.name)

        if existing_role:
            raise BadRequestError("Role name already exists")

        permissions = self._get_permissions_by_ids(data.permission_ids)

        role = Role(
            name=data.name,
            description=data.description,
            is_active=True,
            is_system=False,
            permissions=permissions,
        )

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        return role

    def update_role(
        self,
        role_id: str,
        data: RoleUpdate,
    ) -> Role:
        role = self.get_role_or_404(role_id)

        update_data = data.model_dump(exclude_unset=True)

        if role.is_system:
            if "name" in update_data and update_data["name"] != role.name:
                raise BadRequestError("Cannot rename a system role")

        if "name" in update_data:
            existing_role = self.get_role_by_name(update_data["name"])

            if existing_role and existing_role.id != role.id:
                raise BadRequestError("Role name already exists")

        if "permission_ids" in update_data:
            permission_ids = update_data.pop("permission_ids")

            if permission_ids is not None:
                role.permissions = self._get_permissions_by_ids(permission_ids)

        for field, value in update_data.items():
            setattr(role, field, value)

        self.db.commit()
        self.db.refresh(role)

        return role

    def delete_role(self, role_id: str) -> None:
        role = self.get_role_or_404(role_id)

        if role.is_system:
            raise BadRequestError("Cannot delete a system role")

        self.db.delete(role)
        self.db.commit()

    def assign_permissions_to_role(
        self,
        role_id: str,
        permission_ids: list[str],
    ) -> Role:
        role = self.get_role_or_404(role_id)

        role.permissions = self._get_permissions_by_ids(permission_ids)

        self.db.commit()
        self.db.refresh(role)

        return role

    def _get_permissions_by_ids(
        self,
        permission_ids: list[str],
    ) -> list[Permission]:
        if not permission_ids:
            return []

        permissions = (
            self.db.query(Permission)
            .filter(Permission.id.in_(permission_ids))
            .all()
        )

        if len(permissions) != len(set(permission_ids)):
            raise BadRequestError("Some permissions do not exist")

        return permissions