import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    source = Column(
        Enum("system", "manual", name="rule_source"), nullable=False, default="manual"
    )
    is_active = Column(Boolean, default=True, nullable=False)
    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=False,
    )

    column_name = Column(String(255), nullable=False)
    constraint_name = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    current_value = Column(String(255), nullable=True)
    suggesting_rule = Column(String(255), nullable=True)
    code_for_constraint = Column(String(512), nullable=False)
    rule_description = Column(Text, nullable=True)
    frequency = Column(Integer, nullable=False, default=1)

    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    table = relationship("Table", back_populates="rules")

    verification_results = relationship(
        "RuleVerify", back_populates="rule", cascade="all, delete-orphan"
    )

    # One-way relationship to User
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
        Index("ix_rules__table_status", "table_id", "is_active"),
        Index("ix_rules__table_severity", "table_id", "severity_level"),
        Index("ix_rules__table_source_status", "table_id", "source", "is_active"),
    )


class RuleVerify(Base):
    __tablename__ = "rule_verify"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    rule_id = Column(
        UUID(as_uuid=False), ForeignKey("rules.id", ondelete="CASCADE"), nullable=False
    )

    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=False,
    )

    constraint = Column(String(512), nullable=True)
    constraint_status = Column(String(50), nullable=False)
    constraint_message = Column(Text, nullable=True)

    is_resolved = Column(Boolean, default=False, nullable=False)

    resolved_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    processing_date_hour = Column(DateTime, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    rule = relationship("Rule", back_populates="verification_results")

    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index(
            "ix_rule_verify__rule_hour_unique",
            "rule_id",
            "processing_date_hour",
            unique=True,
        ),
        Index("ix_rule_verify__rule_hour", "rule_id", "processing_date_hour"),
        Index(
            "ix_rule_verify__status_hour", "constraint_status", "processing_date_hour"
        ),
        Index("ix_rule_verify__resolved_by", "resolved_by"),
        Index("ix_rule_verify__is_resolved", "is_resolved"),
    )
