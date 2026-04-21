from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL   # import trực tiếp

# Engine (kết nối DB)
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(
    autoflush=False,
    bind=engine,
)

def get_db():
    """
    Fast API dependence
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()