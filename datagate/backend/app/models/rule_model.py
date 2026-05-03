import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source = Column(
        Enum("system", "manual", name="rule_source"),
        nullable=False,
        default="manual",
    )

    status = Column(
        Enum("pending", "active", "inactive", name="rule_status"),
        nullable=False,
        default="active",
    )

    column_name = Column(String(255), nullable=False)

    constraint_type = Column(
        Enum(
            "not_null",
            "non_negative",
            "unique",
            "value_range",
            "range_check",
            "regex",
            name="constraint_type",
        ),
        nullable=False,
    )

    description = Column(Text, nullable=True)

    value_set = Column(Text, nullable=True)
    regex_pattern = Column(String(1024), nullable=True)
    rule_signature = Column(String(64), nullable=True)
    frequency = Column(Integer, nullable=False, default=1)
    first_seen_at_date_hour = Column(String(30), nullable=True)
    last_seen_at_date_hour = Column(String(30), nullable=True)

    constraint_name = Column(String(512), nullable=True)
    current_value = Column(String(255), nullable=True)
    suggesting_rule = Column(String(255), nullable=True)
    code_for_constraint = Column(String(512), nullable=True)
    suggested_at_date_hour = Column(String(30), nullable=True)

    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    last_modified_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    table = relationship(
        "Table",
        back_populates="rules",
    )

    verification_results = relationship(
        "RuleVerificationResult",
        back_populates="rule",
        cascade="all, delete-orphan",
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_rules",
    )

    last_modified_by_user = relationship(
        "User",
        foreign_keys=[last_modified_by],
    )

    __table_args__ = (
        Index("ix_rules_table_column", "table_id", "column_name"),
        Index("ix_rules_table_status", "table_id", "status"),
        Index("ix_rules_table_signature", "table_id", "rule_signature"),
        Index(
            "uq_rules_table_source_signature",
            "table_id",
            "source",
            "rule_signature",
            unique=True,
            postgresql_where=text("rule_signature IS NOT NULL"),
        ),
    )
