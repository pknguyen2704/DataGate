"""Reset and seed the DataGate database."""

import argparse
import os

from sqlalchemy.orm import Session, selectinload

from app.db.base import Base
from app.db.session import SessionLocal
from app.models import User, Role, Permission
from app.core.security import get_password_hash
from app.rbac.permissions import ALL_PERMISSIONS
from app.rbac.roles import DEFAULT_ROLE_PERMISSIONS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed or reset the DataGate database."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing application data before seeding defaults again.",
    )
    return parser.parse_args()


def reset_database(db: Session) -> None:
    print("Resetting DataGate application tables...")

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())

    db.commit()
    print(f"   Cleared {len(Base.metadata.sorted_tables)} tables")


def seed(db: Session) -> None:
    admin_password = os.getenv("DATAGATE_ADMIN_PASSWORD", "admin123")

    print("Seeding permissions...")
    perm_map: dict[str, Permission] = {}

    for perm_data in ALL_PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            perm = Permission(
                code=perm_data["code"],
                name=perm_data["name"],
                group=perm_data["group"],
                description=perm_data.get("description"),
            )
            db.add(perm)
            perm_map[perm_data["code"]] = perm
        else:
            existing.name = perm_data["name"]
            existing.group = perm_data["group"]
            existing.description = perm_data.get("description")
            perm_map[perm_data["code"]] = existing

    db.flush()
    print(f"   {len(ALL_PERMISSIONS)} permissions seeded")

    print("Seeding roles...")
    role_map: dict[str, Role] = {}

    for role_name, perm_codes in DEFAULT_ROLE_PERMISSIONS.items():
        existing = (
            db.query(Role)
            .options(selectinload(Role.permissions))
            .filter(Role.name == role_name)
            .first()
        )
        if not existing:
            role = Role(
                name=role_name,
                description=f"System-defined {role_name} role",
                is_system=True,
                is_active=True,
                permissions=[],
            )
            db.add(role)
            role_map[role_name] = role
        else:
            existing.description = existing.description or f"System-defined {role_name} role"
            existing.is_system = True
            existing.is_active = True
            role_map[role_name] = existing

    db.flush()

    for role_name, perm_codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = role_map[role_name]
        role.permissions = [
            perm_map[code]
            for code in perm_codes
            if code in perm_map
        ]

    db.flush()
    print(f"   {len(DEFAULT_ROLE_PERMISSIONS)} roles seeded")

    print("Seeding admin user...")
    admin_user = (
        db.query(User)
        .options(selectinload(User.roles))
        .filter(User.username == "admin")
        .first()
    )

    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@datagate.io",
            hashed_password=get_password_hash(admin_password),
            full_name="DataGate Admin",
            is_active=True,
            roles=[],
        )
        db.add(admin_user)
        db.flush()

        admin_role = role_map.get("Admin")
        if admin_role:
            admin_user.roles.append(admin_role)

        if "DATAGATE_ADMIN_PASSWORD" in os.environ:
            print("   Admin user created (username: admin, password: DATAGATE_ADMIN_PASSWORD)")
        else:
            print("   Admin user created (username: admin, password: admin123)")
    else:
        admin_user.email = "admin@datagate.io"
        admin_user.full_name = "DataGate Admin"
        admin_user.hashed_password = get_password_hash(admin_password)
        admin_user.is_active = True
        admin_user.roles = []
        admin_role = role_map.get("Admin")
        if admin_role:
            admin_user.roles.append(admin_role)
        print("   Admin user refreshed")

    db.commit()
    print("Seeding complete.")


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        if args.reset:
            reset_database(db)
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
