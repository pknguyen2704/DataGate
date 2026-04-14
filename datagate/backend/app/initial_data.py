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

    # Check if superuser already exists
    user = db.query(models.User).filter(models.User.email == "admin@datagate.ai").first()
    if not user:
        # Create Superuser
        user_in = models.User(
            email="admin@datagate.ai",
            hashed_password=security.get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )
        db.add(user_in)
        
        # Create default roles
        admin_role = models.Role(name="ADMIN", description="Platform Administrator")
        owner_role = models.Role(name="DATA_OWNER", description="Data Asset Owner")
        viewer_role = models.Role(name="VIEWER", description="Data Consumer / Viewer")
        
        db.add(admin_role)
        db.add(owner_role)
        db.add(viewer_role)
        
        db.commit()
        db.refresh(user_in)
        
        # Assign ADMIN role to the superuser
        user_in.roles.append(admin_role)
        db.commit()
        
        logger.info("Database initialized with superuser: admin@datagate.ai / admin123")
    else:
        logger.info("Database already initialized.")

def main() -> None:
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
