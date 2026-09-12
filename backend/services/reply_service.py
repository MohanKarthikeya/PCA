"""
ReplyService — create, save, and manage AI-generated replies.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.reply import Reply
from utils.exceptions import MessageNotFoundError


class ReplyService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_draft(
        self,
        message_id: str,
        generated_reply: str,
    ) -> Reply:
        """Save an AI-generated reply as a draft."""
        # Remove existing draft if one exists (idempotent)
        existing = await self._get_by_message(message_id)
        if existing:
            existing.generated_reply = generated_reply  # type: ignore[assignment]
            existing.status = "draft"  # type: ignore[assignment]
            await self._db.flush()
            return existing

        reply = Reply(
            message_id=message_id,
            generated_reply=generated_reply,
            status="draft",
        )
        self._db.add(reply)
        await self._db.flush()
        await self._db.refresh(reply)
        return reply

    async def approve(
        self,
        message_id: str,
        final_reply: str,
    ) -> Reply:
        """User approves (and optionally edits) the draft reply."""
        reply = await self._get_by_message(message_id)
        if reply is None:
            raise MessageNotFoundError(message_id)

        reply.final_reply = final_reply  # type: ignore[assignment]
        reply.status = "approved"  # type: ignore[assignment]
        await self._db.flush()
        return reply

    async def mark_sent(self, message_id: str) -> Reply:
        reply = await self._get_by_message(message_id)
        if reply is None:
            raise MessageNotFoundError(message_id)
        reply.status = "sent"  # type: ignore[assignment]
        await self._db.flush()
        return reply

    async def _get_by_message(self, message_id: str) -> Reply | None:
        result = await self._db.execute(
            select(Reply).where(Reply.message_id == message_id)
        )
        return result.scalar_one_or_none()
