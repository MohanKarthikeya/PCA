"""Sender ORM model — represents a contact/conversation partner."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.message import Message
    from models.memory import Memory


class Sender(Base):
    __tablename__ = "senders"

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(60), nullable=False, default="personal"
    )  # personal | work | service | family | other
    default_language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en"
    )
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Free-form JSON bag for extra sender metadata (phone, email, notes, etc.)
    profile_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="sender", cascade="all, delete-orphan"
    )
    memory: Mapped["Memory | None"] = relationship(
        "Memory", back_populates="sender", uselist=False, cascade="all, delete-orphan"
    )
