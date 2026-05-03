from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config


engine = create_engine(
    config.database_url,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()