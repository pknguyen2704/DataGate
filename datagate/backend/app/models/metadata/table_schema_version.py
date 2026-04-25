from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class TableSchemaVersion(Base):
    """
    Model lưu một version schema của một Lakehouse table.

    Mỗi khi collect column metadata:
    - Backend tạo schema_hash từ danh sách cột.
    - Nếu schema_hash chưa tồn tại => insert schema version mới.
    - Nếu schema_hash đã tồn tại => update last_seen_at.
    - Schema version hiện tại của table sẽ có is_current = True.

    Lưu ý:
    - Không dùng schema_id.
    - schema_hash là định danh chính để phát hiện schema thay đổi.
    """

    __tablename__ = "table_schema_version"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Snapshot mà schema này được phát hiện
    snapshot_id = Column(BigInteger, nullable=True)

    # Hash đại diện cho cấu trúc schema
    schema_hash = Column(String, nullable=False)

    column_count = Column(Integer, nullable=False)

    is_current = Column(Boolean, nullable=False, default=False)

    columns_json = Column(JSON, nullable=True)

    first_seen_at = Column(DateTime(timezone=True), nullable=False, default=now())
    last_seen_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    table = relationship(
        "Table",
        back_populates="schema_versions",
    )

    columns = relationship(
        "TableSchemaDetail",
        back_populates="schema_version",
        cascade="all, delete-orphan",
        order_by="TableSchemaDetail.ordinal_position",
    )

    table_metadata = relationship(
        "TableMetadata",
        back_populates="schema_version",
    )

    new_change_events = relationship(
        "TableSchemaChangeEvent",
        back_populates="new_schema_version",
        foreign_keys="TableSchemaChangeEvent.new_schema_version_id",
    )

    old_change_events = relationship(
        "TableSchemaChangeEvent",
        back_populates="old_schema_version",
        foreign_keys="TableSchemaChangeEvent.old_schema_version_id",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "schema_hash",
            name="uq_table_schema_version_table_hash",
        ),
        Index("idx_table_schema_version_table", "table_id"),
        Index("idx_table_schema_version_current", "table_id", "is_current"),
        Index("idx_table_schema_version_snapshot", "table_id", "snapshot_id"),
        Index("idx_table_schema_version_first_seen", "table_id", "first_seen_at"),
        Index("idx_table_schema_version_last_seen", "table_id", "last_seen_at"),
    )