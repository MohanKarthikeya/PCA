"""Pydantic schemas for Message."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    sender_id: str
    text: str
    language: str = "en"
    is_from_user: bool = False


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    is_read: bool
    is_replied: bool
