from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Any
from app.core.config import settings

# Khởi tạo engine kết nối
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Khởi tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Tự động tạo tên bảng dựa trên tên class (viết thường)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
