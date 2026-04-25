from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class Connection(Base):
    """
    Model đại diện cho kết nối của hệ thống tới Data Lakehouse, ví dụ Trino.
    """

    __tablename__ = "connection"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    connection_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now(),
        onupdate=now(),
    )

    # RELATIONSHIPS
    tables = relationship(
        "Table",
        back_populates="connection",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_connection_name",
        ),
        Index(
            "idx_connection_name",
            "name",
        ),
    )