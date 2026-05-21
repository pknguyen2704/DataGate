from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Role, User
from app.core.security import get_hashed_password
from app.rbac.roles import DEFAULT_ROLE_PERMISSIONS


def seed_roles(db: Session) -> dict[str, Role]:
    roles = {}

    for name, codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.name == name).first()

        if not role:
            role = Role(
                name=name,
                description=f"System-defined {name} role",
                permissions=list(codes),
            )
            db.add(role)
        else:
            # Keep default system role permissions in sync
            role.description = role.description or f"System-defined {name} role"
            role.permissions = list(codes)

        roles[name] = role

    db.flush()
    return roles


def seed_default_users(db: Session, roles: dict[str, Role]) -> None:
    default_users = [
        {
            "username": "admin",
            "email": "admin@datagate.io.vn",
            "full_name": "DataGate Admin",
            "password": "admin123@",
            "role_name": "Admin",
        },
        {
            "username": "engineer",
            "email": "engineer@datagate.io.vn",
            "full_name": "DataGate Data Engineer",
            "password": "engineer123@",
            "role_name": "Data Engineer",
        },
        {
            "username": "analyst",
            "email": "analyst@datagate.io.vn",
            "full_name": "DataGate Data Analyst",
            "password": "analyst123@",
            "role_name": "Data Analyst",
        },
    ]

    for user_data in default_users:
        user = db.query(User).filter(User.username == user_data["username"]).first()

        if not user:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_hashed_password(user_data["password"]),
                role=roles.get(user_data["role_name"]),
            )
            db.add(user)
        else:
            # Do not reset password if user already exists
            user.email = user.email or user_data["email"]
            user.full_name = user.full_name or user_data["full_name"]

            # Only assign default role if user has no role
            if user.role_id is None:
                user.role = roles.get(user_data["role_name"])

    db.flush()


def seed(db: Session) -> None:
    roles = seed_roles(db)
    seed_default_users(db, roles)
    db.commit()


def main() -> None:
    db = SessionLocal()

    try:
        seed(db)
        print("Initial DataGate database complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()