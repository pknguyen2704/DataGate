import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
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
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source = Column(
        Enum(
            "system",
            "manual",
            name="rule_source",
        ),
        nullable=False,
        default="manual",
        index=True,
    )

    # pending  : rule do hệ thống gợi ý, chờ người dùng duyệt
    # active   : rule đang được dùng để verify
    # inactive : rule đã bị tắt
    status = Column(
        Enum(
            "pending",
            "active",
            "inactive",
            name="rule_status",
        ),
        nullable=False,
        default="pending",
        index=True,
    )

    # Mức độ cảnh báo nếu rule fail
    severity_level = Column(
        Enum(
            "warning",
            "critical",
            name="rule_severity_level",
        ),
        nullable=False,
        default="warning",
        index=True,
    )

    column_name = Column(String(255), nullable=False)

    constraint_name = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)

    # Số lần hệ thống gợi ý lại cùng một rule
    frequency = Column(Integer, nullable=False, default=1)

    current_value = Column(String(255), nullable=True)
    suggesting_rule = Column(String(255), nullable=True)

    # Ví dụ:
    # .isComplete("vendorid")
    # .isNonNegative("trip_distance")
    # .isContainedIn("payment_type", ["1", "2"])
    code_for_constraint = Column(String(512), nullable=True)

    rule_description = Column(Text, nullable=True)

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
        UniqueConstraint(
            "table_id",
            "source",
            "column_name",
            "code_for_constraint",
            name="uq_rules_table_source_column_code",
        ),
        Index(
            "ix_rules_table_column",
            "table_id",
            "column_name",
        ),
        Index(
            "ix_rules_table_status",
            "table_id",
            "status",
        ),
        Index(
            "ix_rules_table_severity",
            "table_id",
            "severity_level",
        ),
        Index(
            "ix_rules_table_source_status",
            "table_id",
            "source",
            "status",
        ),
    )


class RuleVerificationResult(Base):
    __tablename__ = "rule_verification_result"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    rule_id = Column(
        UUID(as_uuid=False),
        ForeignKey("rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    constraint_status = Column(Text, nullable=True)

    constraint_message = Column(Text, nullable=True)

    processing_date_hour = Column(DateTime, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    rule = relationship(
        "Rule",
        back_populates="verification_results",
    )

    __table_args__ = (
        UniqueConstraint(
            "rule_id",
            "processing_date_hour",
            name="uq_rule_verification_rule_hour",
        ),
        Index(
            "ix_rule_verification_rule_hour",
            "rule_id",
            "processing_date_hour",
        ),
        Index(
            "ix_rule_verification_status_hour",
            "constraint_status",
            "processing_date_hour",
        ),
    )