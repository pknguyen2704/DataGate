from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models import Role, User
from app.core.security import get_hashed_password
from app.rbac.roles import DEFAULT_ROLE_PERMISSIONS


def seed_roles(db: Session) -> dict[str, Role]:
    default_role_names = set(DEFAULT_ROLE_PERMISSIONS)
    roles = {}
    for name, codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = (
            db.query(Role)
            .filter(Role.name == name)
            .first()
        )
        if not role:
            role = Role(name=name)
            db.add(role)
        role.description = role.description or f"System-defined {name} role"
        role.permissions = list(codes)
        roles[name] = role
    db.flush()

    fallback_role = roles["Data Analyst"]
    db.query(User).filter(
        or_(
            User.role_id.is_(None),
            User.role.has(~Role.name.in_(default_role_names)),
        )
    ).update({User.role_id: fallback_role.id}, synchronize_session=False)
    db.flush()

    db.query(Role).filter(~Role.name.in_(default_role_names)).delete(
        synchronize_session=False
    )
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
            .options(selectinload(User.role))
            .filter(User.username == user_data["username"])
            .first()
        )
        if not user:
            user = User(username=user_data["username"])
            db.add(user)
        user.email = user_data["email"]
        user.full_name = user_data["full_name"]
        user.hashed_password = get_hashed_password(user_data["password"])
        role_name = user_data["role_name"]
        user.role = roles[role_name] if role_name in roles else None

    db.flush()


def seed(db: Session) -> None:
    roles = seed_roles(db)
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
