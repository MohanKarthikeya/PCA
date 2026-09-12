"""Reply ORM model — stores AI-generated and user-approved replies."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.message import Message


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Reply(Base):
    __tablename__ = "replies"

    message_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Raw AI-generated reply (in sender's language)
    generated_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Final reply after user edits/approval
    final_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Status: "draft" | "approved" | "sent"
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relationship
    message: Mapped["Message"] = relationship("Message", back_populates="reply")
