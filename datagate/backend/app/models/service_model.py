from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base import Base

class Service(Base):
    """
    Model đại diện cho một kết nối cơ sở dữ liệu (Database Service).
    Lưu trữ cấu hình kết nối và trạng thái giám sát.
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    service_type = Column(String)                   # Loại DB: postgres, trino, mysql...
    connection_url = Column(String)                 # Chuỗi kết nối bảo mật

    # QUẢN LÝ TRẠNG THÁI & XOÁ MỀM
    is_active = Column(Boolean, default=True)       # Trạng thái hoạt động
    integrated_tables = Column(JSON, nullable=True) # Danh sách các bảng đã đăng ký giám sát
    
    # QUAN HỆ (RELATIONSHIPS)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

    # TIMESTAMPS
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime, default=now(), onupdate=now())
