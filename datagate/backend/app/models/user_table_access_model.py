import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class UserTableAccess(Base):
    __tablename__ = "user_table_accesses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    granted_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="table_accesses",
    )

    table = relationship(
        "Table",
        back_populates="user_accesses",
    )

    granter = relationship(
        "User",
        foreign_keys=[granted_by],
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "table_id",
            name="uq_user_table_accesses_user_table",
        ),
    )