"""
MessageService — all database operations for messages.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message
from schemas.message import MessageCreate
from utils.exceptions import MessageNotFoundError


class MessageService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, data: MessageCreate) -> Message:
        msg = Message(
            sender_id=data.sender_id,
            text=data.text,
            language=data.language,
            is_from_user=data.is_from_user,
        )
        self._db.add(msg)
        await self._db.flush()
        await self._db.refresh(msg)
        return msg

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .order_by(Message.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_sender(self, sender_id: str, limit: int = 50) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .where(Message.sender_id == sender_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_unread(self, sender_id: str | None = None) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.is_read == False, Message.is_from_user == False)  # noqa: E712
            .order_by(Message.timestamp.asc())
        )
        if sender_id:
            stmt = stmt.where(Message.sender_id == sender_id)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, message_id: str) -> Message:
        result = await self._db.execute(
            select(Message).where(Message.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg is None:
            raise MessageNotFoundError(message_id)
        return msg

    async def mark_read(self, message_id: str) -> Message:
        msg = await self.get_by_id(message_id)
        msg.is_read = True  # type: ignore[assignment]
        await self._db.flush()
        return msg

    async def mark_replied(self, message_id: str) -> Message:
        msg = await self.get_by_id(message_id)
        msg.is_replied = True  # type: ignore[assignment]
        msg.is_read = True  # type: ignore[assignment]
        await self._db.flush()
        return msg

    async def mark_many_read(self, message_ids: list[str]) -> None:
        for mid in message_ids:
            try:
                await self.mark_read(mid)
            except MessageNotFoundError:
                pass  # Skip silently for batch operations
