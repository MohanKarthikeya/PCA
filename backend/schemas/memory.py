"""Pydantic schemas for Memory."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sender_id: str
    summary: str | None
    key_facts: dict[str, Any] | None
    pending_actions: list[str] | None
    last_interaction: datetime | None
