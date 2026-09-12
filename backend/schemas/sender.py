"""Pydantic schemas for Sender."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SenderBase(BaseModel):
    name: str
    category: str = "personal"
    default_language: str = "en"
    avatar: str | None = None
    profile_info: dict[str, Any] | None = None


class SenderCreate(SenderBase):
    pass


class SenderUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    default_language: str | None = None
    avatar: str | None = None
    profile_info: dict[str, Any] | None = None


class SenderResponse(SenderBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
