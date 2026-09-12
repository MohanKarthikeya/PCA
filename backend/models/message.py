"""Message ORM model — a single message in a conversation thread."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.sender import Sender
    from models.reply import Reply


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Message(Base):
    __tablename__ = "messages"

    sender_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("senders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Raw message text
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Detected or declared language code (e.g. "en", "te", "hi")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    # False = incoming message from sender; True = outgoing message from user
    is_from_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_replied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    sender: Mapped["Sender"] = relationship("Sender", back_populates="messages")
    reply: Mapped["Reply | None"] = relationship(
        "Reply", back_populates="message", uselist=False, cascade="all, delete-orphan"
    )
