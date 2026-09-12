"""
Pydantic schemas for the PCA orchestrator endpoints:
  POST /pca/wake   → AI Call #1 (message analysis)
  POST /pca/reply  → AI Call #2 (reply generation)
"""

from typing import Any

from pydantic import BaseModel, Field


# ── Wake PCA (/pca/wake) ──────────────────────────────────────────────────────

class WakeRequest(BaseModel):
    """
    Optional filters for the wake call.
    If sender_id is provided, only that sender's unread messages are analyzed.
    """
    sender_id: str | None = Field(
        default=None,
        description="Analyze only this sender's messages. Omit for global analysis."
    )


class MessageAnalysis(BaseModel):
    """Per-message analysis result returned by the AI."""
    message_id: str
    detected_language: str
    translated_message: str
    intent: str
    importance_score: float = Field(ge=0.0, le=10.0)
    telugu_explanation: str
    reply_required: bool
    suggested_action: str


class MemoryUpdate(BaseModel):
    sender_id: str
    summary: str
    key_facts: dict[str, Any]
    pending_actions: list[str]


class WakeResponse(BaseModel):
    """Structured response from AI Call #1."""
    provider_used: str
    messages_analyzed: int
    analyses: list[MessageAnalysis]
    memory_updates: list[MemoryUpdate]
    greeting: str            # Telugu greeting shown in PCA UI
    summary_telugu: str      # Overall summary for user in Telugu


# ── Reply PCA (/pca/reply) ────────────────────────────────────────────────────

class ReplyRequest(BaseModel):
    message_id: str = Field(description="The message to reply to.")
    user_instruction: str = Field(
        description="User's instruction, e.g. 'Tell him I'll be there at 5 PM'."
    )


class ReplyResponse(BaseModel):
    """Structured response from AI Call #2."""
    provider_used: str
    message_id: str
    reply_in_sender_language: str
    reply_translation: str      # Translation back to user's preferred language
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str | None = None
    reply_id: str               # ID of the saved Reply record
