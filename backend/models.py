
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String,func,JSON,Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    short_code: Mapped[str] = mapped_column(
        String(6), unique=True, nullable=False
    )

    original_url: Mapped[str] = mapped_column(
        String(2048), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    clicks: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )


class ProcessedBatch(Base):
    __tablename__ = "processed_batches"

    batch_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
