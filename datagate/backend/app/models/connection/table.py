from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class Table(Base):
    """
    Model đại diện cho các bảng lakehouse đã được phát hiện và đăng ký
    từ connection để phục vụ quản lý, observability và data quality.
    """

    __tablename__ = "table"
    id = Column(BigInteger, primary_key=True, index=True)
    connection_id = Column(
        BigInteger,
        ForeignKey("connection.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    catalog_name = Column(String, nullable=False, default="iceberg")
    schema_name = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now(),
        onupdate=now(),
    )

    # RELATIONSHIPS
    connection = relationship(
        "Connection",
        back_populates="tables",
    )

    table_metadata = relationship(
        "TableMetadata",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    schema_versions = relationship(
        "TableSchemaVersion",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    schema_change_events = relationship(
        "TableSchemaChangeEvent",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "catalog_name",
            "schema_name",
            "table_name",
            name="uq_table_connection_catalog_schema_table",
        ),
        Index(
            "idx_table_connection_id",
            "connection_id",
        ),
        Index(
            "idx_table_catalog_schema_table",
            "catalog_name",
            "schema_name",
            "table_name",
        ),
        Index(
            "idx_table_schema_name",
            "schema_name",
        ),
        Index(
            "idx_table_table_name",
            "table_name",
        ),
        Index(
            "idx_table_is_active",
            "is_active",
        ),
    )