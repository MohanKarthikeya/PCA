"""
Memory ORM model.
Stores conversation context per sender as structured JSON inside SQLite.
No vector database required.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.sender import Sender


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Memory(Base):
    __tablename__ = "memory"

    sender_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("senders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # one memory record per sender
        index=True,
    )
    # Short natural-language summary of the relationship / recent exchanges
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Structured facts: {"topics": [...], "preferences": {...}, ...}
    key_facts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # List of action strings the user still needs to act on
    pending_actions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # When was this memory last refreshed by an AI call
    last_interaction: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    sender: Mapped["Sender"] = relationship("Sender", back_populates="memory")
