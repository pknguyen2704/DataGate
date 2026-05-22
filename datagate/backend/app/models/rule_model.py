import uuid
from sqlalchemy import Boolean, Column,DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

    source = Column(String(50), nullable=False, default="manual")
    is_active = Column(Boolean, default=True, nullable=False)
    severity_level = Column(String(50), nullable=False, default="warning")

    column_name = Column(String(255), nullable=True)
    constraint_name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    current_value = Column(Text, nullable=True)
    suggesting_rule = Column(Text, nullable=True)
    code_for_constraint = Column(Text, nullable=False)
    frequency = Column(Integer, nullable=False, default=1)

    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_modified_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    table = relationship("Table", back_populates="rules")

    quality_check_results = relationship(
        "QualityCheckResult", back_populates="rule"
    )

    created_by_user = relationship("User", foreign_keys=[created_by])

    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index(
            "ix_rules__table_source_column_code",
            "table_id",
            "source",
            "column_name",
            "code_for_constraint",
            unique=True,
        ),
        Index("ix_rules__table_column", "table_id", "column_name"),
        Index("ix_rules__table_active", "table_id", "is_active"),
        Index("ix_rules__table_severity", "table_id", "severity_level"),
    )
