import logging
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import security
from app.db.session import SessionLocal, engine
from app.db.base_class import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)

    admin_role = db.query(models.Role).filter(models.Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = models.Role(name="ADMIN", description="Platform Administrator")
        db.add(admin_role)

    owner_role = db.query(models.Role).filter(models.Role.name == "DATA_OWNER").first()
    if not owner_role:
        owner_role = models.Role(name="DATA_OWNER", description="Data Asset Owner")
        db.add(owner_role)

    viewer_role = db.query(models.Role).filter(models.Role.name == "VIEWER").first()
    if not viewer_role:
        viewer_role = models.Role(name="VIEWER", description="Data Consumer / Viewer")
        db.add(viewer_role)

    db.commit()

    # Check if superuser already exists
    user = db.query(models.User).filter(models.User.email == "admin@datagate.ai").first()
    if not user:
        # Create Superuser
        user_in = models.User(
            email="admin@datagate.ai",
            username="admin",
            hashed_password=security.get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )
        db.add(user_in)
        
        db.add(user_in)
        db.commit()
        db.refresh(user_in)
        
        # Assign ADMIN role to the superuser
        user_in.roles.append(admin_role)
        db.commit()
        
        logger.info("Database initialized with superuser: admin@datagate.ai / admin123")
    else:
        logger.info("Database already initialized.")

    sample_users = [
        {
            "email": "owner.a@datagate.ai",
            "username": "owner_a",
            "password": "owner123",
            "full_name": "Owner A",
            "is_superuser": False,
            "role": owner_role,
        },
        {
            "email": "viewer.b@datagate.ai",
            "username": "viewer_b",
            "password": "viewer123",
            "full_name": "Viewer B",
            "is_superuser": False,
            "role": viewer_role,
        },
    ]

    for sample_user in sample_users:
        existing_user = db.query(models.User).filter(models.User.email == sample_user["email"]).first()
        if existing_user:
            if sample_user["role"] not in existing_user.roles:
                existing_user.roles.append(sample_user["role"])
                db.add(existing_user)
                db.commit()
            continue

        created_user = models.User(
            email=sample_user["email"],
            username=sample_user["username"],
            hashed_password=security.get_password_hash(sample_user["password"]),
            full_name=sample_user["full_name"],
            is_active=True,
            is_superuser=sample_user["is_superuser"],
        )
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        created_user.roles.append(sample_user["role"])
        db.add(created_user)
        db.commit()

def main() -> None:
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
