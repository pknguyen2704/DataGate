import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class RuleVerificationResult(Base):
    __tablename__ = "rule_verification_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    rule_id = Column(
        UUID(as_uuid=False),
        ForeignKey("rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_date_hour = Column(String(30), nullable=False)
    verification_status = Column(
        Enum("passed", "failed", "error", name="rule_verification_status"),
        nullable=False,
    )
    actual_value = Column(String(255), nullable=True)
    expected_value = Column(String(255), nullable=True)
    failure_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rule = relationship("Rule", back_populates="verification_results")
    table = relationship("Table", back_populates="rule_verification_results")

    __table_args__ = (
        UniqueConstraint("rule_id", "batch_date_hour", name="uq_rule_verification_rule_batch"),
        Index("ix_rule_verification_table_batch", "table_id", "batch_date_hour"),
    )
