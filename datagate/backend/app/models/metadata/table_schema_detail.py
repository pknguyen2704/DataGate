from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class TableSchemaDetail(Base):
    """
    Model lưu chi tiết từng cột của một schema version.

    UI dùng bảng này để hiển thị:
    - Column name
    - Data type
    - Nullable
    - Position
    - Partition column hay không
    """

    __tablename__ = "table_schema_detail"

    id = Column(BigInteger, primary_key=True, index=True)

    schema_version_id = Column(
        BigInteger,
        ForeignKey("table_schema_version.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    column_name = Column(String, nullable=False)
    column_type = Column(String, nullable=False)
    ordinal_position = Column(Integer, nullable=False)

    # Giữ String nếu lấy trực tiếp từ information_schema.columns: YES/NO
    is_nullable = Column(String, nullable=True)

    column_default = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)

    is_partition_column = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    schema_version = relationship(
        "TableSchemaVersion",
        back_populates="columns",
    )

    __table_args__ = (
        UniqueConstraint(
            "schema_version_id",
            "column_name",
            name="uq_table_schema_detail_schema_version_column",
        ),
        Index("idx_table_schema_detail_version", "schema_version_id", "ordinal_position"),
        Index("idx_table_schema_detail_name", "column_name"),
        Index("idx_table_schema_detail_type", "column_type"),
        Index("idx_table_schema_detail_partition", "schema_version_id", "is_partition_column"),
    )