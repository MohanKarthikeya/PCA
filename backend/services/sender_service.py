"""
SenderService — manage sender profiles.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sender import Sender
from schemas.sender import SenderCreate, SenderUpdate
from utils.exceptions import SenderNotFoundError


class SenderService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, data: SenderCreate) -> Sender:
        sender = Sender(
            name=data.name,
            category=data.category,
            default_language=data.default_language,
            avatar=data.avatar,
            profile_info=data.profile_info,
        )
        self._db.add(sender)
        await self._db.flush()
        await self._db.refresh(sender)
        return sender

    async def get_all(self) -> list[Sender]:
        result = await self._db.execute(
            select(Sender).order_by(Sender.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, sender_id: str) -> Sender:
        result = await self._db.execute(
            select(Sender).where(Sender.id == sender_id)
        )
        sender = result.scalar_one_or_none()
        if sender is None:
            raise SenderNotFoundError(sender_id)
        return sender

    async def update(self, sender_id: str, data: SenderUpdate) -> Sender:
        sender = await self.get_by_id(sender_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(sender, field, value)
        await self._db.flush()
        return sender

    async def delete(self, sender_id: str) -> None:
        sender = await self.get_by_id(sender_id)
        await self._db.delete(sender)
        await self._db.flush()

    async def get_as_dict(self, sender_ids: list[str]) -> dict[str, dict]:
        """Return a dict of sender_id → sender fields for prompt building."""
        senders = {}
        for sid in sender_ids:
            try:
                s = await self.get_by_id(sid)
                senders[sid] = {
                    "name": s.name,
                    "category": s.category,
                    "default_language": s.default_language,
                }
            except SenderNotFoundError:
                pass
        return senders
