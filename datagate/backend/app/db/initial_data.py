import argparse
import os

from sqlalchemy.orm import Session, selectinload

from app.db.base import Base
from app.db.session import SessionLocal
from app.models import Permission, Role, User
from app.core.security import get_hashed_password
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


def reset_database(db: Session) -> int:
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    return len(Base.metadata.sorted_tables)


def seed_permissions(db: Session) -> dict[str, Permission]:
    permissions = {}
    for data in ALL_PERMISSIONS:
        permission = db.query(Permission).filter(Permission.code == data["code"]).first()
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


def seed_admin(db: Session, roles: dict[str, Role]) -> User:
    password = os.getenv("DATAGATE_ADMIN_PASSWORD", "admin123")
    admin = (
        db.query(User)
        .options(selectinload(User.roles))
        .filter(User.username == "admin")
        .first()
    )
    if not admin:
        admin = User(username="admin")
        db.add(admin)
    admin.email = os.getenv("DATAGATE_ADMIN_EMAIL", "admin@datagate.io")
    admin.full_name = os.getenv("DATAGATE_ADMIN_FULL_NAME", "DataGate Admin")
    admin.hashed_password = get_hashed_password(password)
    admin.is_active = True
    admin.roles = [roles["Admin"]] if "Admin" in roles else []
    db.flush()
    return admin


def seed_test_users(db: Session, roles: dict[str, Role]) -> None:
    # Data Engineer
    engineer = db.query(User).filter(User.username == "engineer").first()
    if not engineer:
        engineer = User(
            username="engineer",
            email="engineer@datagate.io",
            full_name="John Engineer",
            hashed_password=get_hashed_password("engineer123"),
            is_active=True,
            roles=[roles["Data Engineer"]] if "Data Engineer" in roles else []
        )
        db.add(engineer)
    
    # Data Analyst
    analyst = db.query(User).filter(User.username == "analyst").first()
    if not analyst:
        analyst = User(
            username="analyst",
            email="analyst@datagate.io",
            full_name="Sarah Analyst",
            hashed_password=get_hashed_password("analyst123"),
            is_active=True,
            roles=[roles["Data Analyst"]] if "Data Analyst" in roles else []
        )
        db.add(analyst)

def seed_data_assets(db: Session) -> None:
    from app.models import Connection, Table
    import uuid

    # Seed Sample Connection
    conn = db.query(Connection).filter(Connection.connection_name == "Sample Data Lake").first()
    if not conn:
        conn = Connection(
            id=str(uuid.uuid4()),
            connection_name="Sample Data Lake",
            connection_type="trino",
            host="localhost",
            port=8080,
            username="admin",
            password="password",
            database="iceberg",
            is_active=True
        )
        db.add(conn)
        db.flush()

    # Seed Sample Tables
    samples = [
        ("iceberg", "silver", "users"),
        ("iceberg", "silver", "orders"),
        ("iceberg", "gold", "customer_summary"),
        ("iceberg", "gold", "daily_sales"),
    ]
    for cat, sch, tab in samples:
        exists = db.query(Table).filter(
            Table.catalog_name == cat,
            Table.schema_name == sch,
            Table.table_name == tab
        ).first()
        if not exists:
            table = Table(
                id=str(uuid.uuid4()),
                connection_id=conn.id,
                catalog_name=cat,
                schema_name=sch,
                table_name=tab,
                is_active=True
            )
            db.add(table)

def seed(db: Session) -> None:
    permissions = seed_permissions(db)
    roles = seed_roles(db, permissions)
    seed_admin(db, roles)
    seed_test_users(db, roles)
    db.commit()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        if args.reset:
            count = reset_database(db)
            print(f"Reset {count} tables")
        seed(db)
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()
