from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models import Permission, Role, User
from app.core.security import get_hashed_password
from app.rbac.permissions import ALL_PERMISSIONS
from app.rbac.roles import DEFAULT_ROLE_PERMISSIONS


def seed_permissions(db: Session) -> dict[str, Permission]:
    valid_codes = [data["code"] for data in ALL_PERMISSIONS]
    db.query(Permission).filter(~Permission.code.in_(valid_codes)).delete(
        synchronize_session=False
    )
    db.flush()

    permissions = {}
    for data in ALL_PERMISSIONS:
        permission = (
            db.query(Permission).filter(Permission.code == data["code"]).first()
        )
        if not permission:
            permission = Permission(code=data["code"])
            db.add(permission)
        permission.name = data["name"]
        permission.permission_group = data.get("group")
        permission.description = data.get("description")
        permissions[data["code"]] = permission
    db.flush()
    return permissions


def seed_roles(db: Session, permissions: dict[str, Permission]) -> dict[str, Role]:
    roles = {}
    for name, codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = (
            db.query(Role)
            .options(selectinload(Role.permissions))
            .filter(Role.name == name)
            .first()
        )
        if not role:
            role = Role(name=name)
            db.add(role)
        role.description = role.description or f"System-defined {name} role"
        role.is_system = True
        role.is_active = True
        role.permissions = [permissions[code] for code in codes if code in permissions]
        roles[name] = role
    db.flush()
    return roles


def seed_default_users(db: Session, roles: dict[str, Role]) -> None:
    default_users = [
        {
            "username": "admin",
            "email": "admin@datagate.io.vn",
            "full_name": "DataGate Admin",
            "password": "admin123",
            "role_name": "Admin",
        },
        {
            "username": "engineer",
            "email": "engineer@datagate.io.vn",
            "full_name": "DataGate Data Engineer",
            "password": "engineer123",
            "role_name": "Data Engineer",
        },
        {
            "username": "analyst",
            "email": "analyst@datagate.io.vn",
            "full_name": "DataGate Data Analyst",
            "password": "analyst123",
            "role_name": "Data Analyst",
        },
    ]

    for user_data in default_users:
        user = (
            db.query(User)
            .options(selectinload(User.roles))
            .filter(User.username == user_data["username"])
            .first()
        )
        if not user:
            user = User(username=user_data["username"])
            db.add(user)
        user.email = user_data["email"]
        user.full_name = user_data["full_name"]
        user.hashed_password = get_hashed_password(user_data["password"])
        user.is_active = True
        role_name = user_data["role_name"]
        user.roles = [roles[role_name]] if role_name in roles else []

    db.flush()


def seed(db: Session) -> None:
    permissions = seed_permissions(db)
    roles = seed_roles(db, permissions)
    seed_default_users(db, roles)
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()
