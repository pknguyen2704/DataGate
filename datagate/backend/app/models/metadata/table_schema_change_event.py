from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class TableSchemaChangeEvent(Base):
    """
    Model lưu từng sự kiện thay đổi schema.

    Ví dụ:
    - COLUMN_ADDED: thêm cột mới
    - COLUMN_REMOVED: xóa cột
    - COLUMN_TYPE_CHANGED: đổi kiểu dữ liệu
    - COLUMN_NULLABILITY_CHANGED: đổi nullable
    - COLUMN_ORDER_CHANGED: đổi thứ tự cột

    Bảng này phục vụ trực tiếp cho UI tab 'Schema Changes'.
    """

    __tablename__ = "table_schema_change_event"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_schema_version_id = Column(
        BigInteger,
        ForeignKey("table_schema_version.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    new_schema_version_id = Column(
        BigInteger,
        ForeignKey("table_schema_version.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Snapshot tại thời điểm phát hiện thay đổi
    snapshot_id = Column(BigInteger, nullable=True)

    change_type = Column(String, nullable=False)

    column_name = Column(String, nullable=True)

    old_column_type = Column(String, nullable=True)
    new_column_type = Column(String, nullable=True)

    old_ordinal_position = Column(Integer, nullable=True)
    new_ordinal_position = Column(Integer, nullable=True)

    old_is_nullable = Column(String, nullable=True)
    new_is_nullable = Column(String, nullable=True)

    change_detail = Column(JSON, nullable=True)

    detected_at = Column(DateTime(timezone=True), nullable=False, default=now(), index=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    table = relationship(
        "Table",
        back_populates="schema_change_events",
    )

    old_schema_version = relationship(
        "TableSchemaVersion",
        back_populates="old_change_events",
        foreign_keys=[old_schema_version_id],
    )

    new_schema_version = relationship(
        "TableSchemaVersion",
        back_populates="new_change_events",
        foreign_keys=[new_schema_version_id],
    )

    __table_args__ = (
        Index("idx_table_schema_change_event_table_time", "table_id", "detected_at"),
        Index("idx_table_schema_change_event_type", "change_type"),
        Index("idx_table_schema_change_event_column", "column_name"),
        Index("idx_table_schema_change_event_snapshot", "snapshot_id"),
    )