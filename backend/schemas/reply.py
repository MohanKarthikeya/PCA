"""Pydantic schemas for Reply."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    generated_reply: str | None
    final_reply: str | None
    status: str
    timestamp: datetime


class ReplyUpdate(BaseModel):
    """Allow user to submit their edited final reply."""
    final_reply: str
    status: str = "approved"
