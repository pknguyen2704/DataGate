import logging
from sqlalchemy.orm import Session
from app import models
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.core.security import get_password_hash
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # 0. Tạo tất cả các bảng nếu chưa tồn tại
    logger.info("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    # 1. Initialize Users
    user = db.query(models.User).filter(models.User.username == "admin").first()
    if not user:
        user = models.User(
            username="admin",
            email="admin@datagate.io",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
            accessible_tables=[] # Khởi tạo rỗng, người dùng sẽ tự cấu hình
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created superuser: {user.username}/admin123")
    else:
        logger.info("Superuser already exists")

    # 2. KHÔNG khởi tạo Connection mặc định
    # Người dùng muốn tự nhập từ UI ban đầu
    logger.info("Skipping default connection seeding (as requested).")

    # 3. Initialize Sample Observability Data (Tùy chọn, giữ lại để UI không trống không)
    table_name = "customer_bronze"
    schema_name = "bronze"
    catalog = "iceberg"

    db.query(models.ObservabilitySnapshot).filter(
        models.ObservabilitySnapshot.table_name == table_name
    ).delete()

    for i in range(30):
        snap_time = datetime.now() - timedelta(days=30-i)
        snap = models.ObservabilitySnapshot(
            table_name=table_name,
            schema_name=schema_name,
            catalog=catalog,
            snapshot_time=snap_time,
            total_records=1000 + (i * 50) + (i % 3 * 20),
            total_size=1024 * 50 * (i + 1),
            last_updated_time=snap_time - timedelta(hours=2)
        )
        db.add(snap)

    db.commit()
    logger.info("Seeding script completed.")

def main() -> None:
    logger.info("Seeding data...")
    db = SessionLocal()
    init_db(db)
    logger.info("Seeding complete.")

if __name__ == "__main__":
    main()
