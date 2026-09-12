"""
MemoryService — store and retrieve per-sender conversation memory.

Memory is stored as structured JSON in SQLite.
No vector database, no external service required.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.memory import Memory
from utils.exceptions import MemoryNotFoundError


class MemoryService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_sender(self, sender_id: str) -> Memory:
        result = await self._db.execute(
            select(Memory).where(Memory.sender_id == sender_id)
        )
        memory = result.scalar_one_or_none()
        if memory is None:
            raise MemoryNotFoundError(sender_id)
        return memory

    async def get_all(self) -> list[Memory]:
        result = await self._db.execute(select(Memory))
        return list(result.scalars().all())

    async def get_or_create(self, sender_id: str) -> Memory:
        """Return existing memory or create a blank one."""
        try:
            return await self.get_by_sender(sender_id)
        except MemoryNotFoundError:
            memory = Memory(
                sender_id=sender_id,
                key_facts={},
                pending_actions=[],
            )
            self._db.add(memory)
            await self._db.flush()
            await self._db.refresh(memory)
            return memory

    async def update(
        self,
        sender_id: str,
        summary: str | None = None,
        key_facts: dict[str, Any] | None = None,
        pending_actions: list[str] | None = None,
    ) -> Memory:
        memory = await self.get_or_create(sender_id)

        if summary is not None:
            memory.summary = summary  # type: ignore[assignment]

        if key_facts is not None:
            # Merge new facts with existing ones
            existing = memory.key_facts or {}
            existing.update(key_facts)
            memory.key_facts = existing  # type: ignore[assignment]

        if pending_actions is not None:
            memory.pending_actions = pending_actions  # type: ignore[assignment]

        memory.last_interaction = datetime.now(timezone.utc)  # type: ignore[assignment]
        await self._db.flush()
        return memory

    async def get_as_dict(self, sender_ids: list[str]) -> dict[str, dict]:
        """Return a dict of sender_id → memory fields for prompt building."""
        result: dict[str, dict] = {}
        for sid in sender_ids:
            try:
                mem = await self.get_by_sender(sid)
                result[sid] = {
                    "summary": mem.summary,
                    "key_facts": mem.key_facts or {},
                    "pending_actions": mem.pending_actions or [],
                }
            except MemoryNotFoundError:
                pass
        return result

    async def apply_ai_updates(
        self, updates: list[dict[str, Any]]
    ) -> None:
        """
        Apply a list of memory_updates dicts returned by the AI analysis.
        Each dict should have: sender_id, summary, key_facts, pending_actions.
        """
        for upd in updates:
            sender_id = upd.get("sender_id")
            if not sender_id:
                continue
            await self.update(
                sender_id=sender_id,
                summary=upd.get("summary"),
                key_facts=upd.get("key_facts"),
                pending_actions=upd.get("pending_actions"),
            )
