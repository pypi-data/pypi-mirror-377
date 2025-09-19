import uuid
from datetime import datetime

from sqlalchemy import JSON as SA_JSON
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from nlbone.adapters.db import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB, UUID

    JSONType = JSONB
    UUIDType = UUID(as_uuid=True)
except Exception:
    JSONType = SA_JSON
    UUIDType = String(36)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType, primary_key=True, default=uuid.uuid4)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    operation: Mapped[str] = mapped_column(String(10), nullable=False)  # INSERT/UPDATE/DELETE
    changes: Mapped[dict | None] = mapped_column(JSONType, nullable=True)

    actor_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_audit_entity_entityid", "entity", "entity_id"),
        Index("ix_audit_created_at", "created_at"),
    )
