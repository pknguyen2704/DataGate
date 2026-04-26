"""
Database seed script — creates default permissions, roles, and admin user.
Run once after migrations: python -m app.db.initial_data
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.auth import User, Role, Permission
from app.core.security import get_password_hash
from app.core.permissions import ALL_PERMISSIONS, DEFAULT_ROLE_PERMISSIONS


async def seed(db: AsyncSession):
    from sqlalchemy import select

    print("🌱 Seeding permissions...")
    perm_map: dict[str, Permission] = {}

    for perm_data in ALL_PERMISSIONS:
        result = await db.execute(select(Permission).where(Permission.code == perm_data["code"]))
        existing = result.scalars().first()
        if not existing:
            perm = Permission(
                id=str(uuid.uuid4()),
                code=perm_data["code"],
                name=perm_data["name"],
                group=perm_data["group"],
            )
            db.add(perm)
            perm_map[perm_data["code"]] = perm
        else:
            perm_map[perm_data["code"]] = existing

    await db.flush()
    print(f"   ✓ {len(ALL_PERMISSIONS)} permissions seeded")

    print("🌱 Seeding roles...")
    role_map: dict[str, Role] = {}

    from sqlalchemy.orm import selectinload

    for role_name, perm_codes in DEFAULT_ROLE_PERMISSIONS.items():
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == role_name)
        )
        existing = result.scalars().first()
        if not existing:
            role = Role(
                id=str(uuid.uuid4()),
                name=role_name,
                description=f"System-defined {role_name} role",
                is_system=True,
                is_active=True,
                permissions=[],
            )
            db.add(role)
            role_map[role_name] = role
        else:
            role_map[role_name] = existing

    await db.flush()

    # Assign permissions to roles
    for role_name, perm_codes in DEFAULT_ROLE_PERMISSIONS.items():
        role = role_map[role_name]
        existing_perm_codes = {p.code for p in role.permissions}
        for code in perm_codes:
            if code in perm_map and code not in existing_perm_codes:
                role.permissions.append(perm_map[code])

    await db.flush()
    print(f"   ✓ {len(DEFAULT_ROLE_PERMISSIONS)} roles seeded")

    print("🌱 Seeding admin user...")
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.username == "admin")
    )
    admin_user = result.scalars().first()

    if not admin_user:
        admin_user = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@datagate.io",
            hashed_password=get_password_hash("admin123"),
            full_name="DataGate Admin",
            is_active=True,
            roles=[],
        )
        db.add(admin_user)
        await db.flush()

        admin_role = role_map.get("Admin")
        if admin_role:
            admin_user.roles.append(admin_role)

        print("   ✓ Admin user created (username: admin, password: admin123)")
    else:
        print("   ℹ Admin user already exists, skipping")

    await db.commit()
    print("✅ Seeding complete!")


async def main():
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
