"""
Shared FastAPI dependencies.

Usage in routers:
    db: AsyncSession = Depends(get_db)
    ai_svc: AIService = Depends(get_ai_service)
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.message_service import MessageService
from services.sender_service import SenderService
from services.memory_service import MemoryService
from services.reply_service import ReplyService
from services.ai_service import AIService


# ── Database session ──────────────────────────────────────────────────────────

# Re-export so routers only need to import from api.deps
__all__ = [
    "get_db",
    "get_message_service",
    "get_sender_service",
    "get_memory_service",
    "get_reply_service",
    "get_ai_service",
]


# ── Service factories ─────────────────────────────────────────────────────────

def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(db)


def get_sender_service(db: AsyncSession = Depends(get_db)) -> SenderService:
    return SenderService(db)


def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(db)


def get_reply_service(db: AsyncSession = Depends(get_db)) -> ReplyService:
    return ReplyService(db)


def get_ai_service() -> AIService:
    return AIService()
