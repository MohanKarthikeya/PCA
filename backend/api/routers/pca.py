"""
PCA Orchestrator Router — the heart of the application.

POST /pca/wake   → AI Call #1: Batch analysis of all unread messages
POST /pca/reply  → AI Call #2: Generate a reply for a specific message

These two endpoints are the only places where AI calls originate.
All other endpoints are purely database operations (no AI calls).
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import (
    get_ai_service,
    get_db,
    get_memory_service,
    get_message_service,
    get_reply_service,
    get_sender_service,
)
from config.settings import get_settings
from schemas.pca import (
    ReplyRequest,
    ReplyResponse as PCAReplyResponse,
    WakeRequest,
    WakeResponse,
)
from services.ai_service import AIService
from services.memory_service import MemoryService
from services.message_service import MessageService
from services.reply_service import ReplyService
from services.sender_service import SenderService
from utils.exceptions import InvalidRequestError

router = APIRouter(prefix="/pca", tags=["PCA Orchestrator"])
log = logging.getLogger("pca.api.pca")
settings = get_settings()


@router.post(
    "/wake",
    response_model=WakeResponse,
    summary="Wake PCA — AI Call #1: Analyze all unread messages",
    description=(
        "Collects all unread messages, gathers relevant memory, builds a single "
        "optimized prompt, performs ONE AI API call, updates memory, marks messages "
        "as read, and returns structured analysis JSON."
    ),
)
async def wake_pca(
    request: WakeRequest,
    db: AsyncSession = Depends(get_db),
    msg_svc: MessageService = Depends(get_message_service),
    sender_svc: SenderService = Depends(get_sender_service),
    mem_svc: MemoryService = Depends(get_memory_service),
    ai_svc: AIService = Depends(get_ai_service),
) -> WakeResponse:
    log.info("POST /pca/wake", extra={"sender_filter": request.sender_id})

    # ── Step 1: Collect unread messages ──────────────────────────────────────
    unread = await msg_svc.get_unread(sender_id=request.sender_id)

    if not unread:
        log.info("No unread messages found")
        return WakeResponse(
            provider_used=settings.ACTIVE_PROVIDER,
            messages_analyzed=0,
            analyses=[],
            memory_updates=[],
            greeting="నమస్కారం! మీకు కొత్త సందేశాలు ఏమీ లేవు.",
            summary_telugu="అన్ని సందేశాలు చదివారు. కొత్త సందేశాలు ఏమీ లేవు.",
        )

    # ── Step 2: Gather sender profiles ───────────────────────────────────────
    sender_ids = list({msg.sender_id for msg in unread})
    senders_dict = await sender_svc.get_as_dict(sender_ids)

    # ── Step 3: Gather relevant memory ───────────────────────────────────────
    memory_dict = await mem_svc.get_as_dict(sender_ids)

    # ── Step 4: Serialize messages for prompt ────────────────────────────────
    messages_data = [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "text": msg.text,
            "language": msg.language,
            "timestamp": msg.timestamp.isoformat(),
            "is_from_user": msg.is_from_user,
        }
        for msg in unread
    ]

    # ── Step 5: Single AI call ───────────────────────────────────────────────
    # (This is the ONLY AI call in the wake flow)
    wake_response = await ai_svc.analyze_messages(
        messages=messages_data,
        senders=senders_dict,
        memory=memory_dict,
        user_language="en",  # Future: load from user preferences
    )

    # ── Step 6: Persist memory updates ───────────────────────────────────────
    if wake_response.memory_updates:
        await mem_svc.apply_ai_updates(
            [upd.model_dump() for upd in wake_response.memory_updates]
        )

    # ── Step 7: Mark analysed messages as read ────────────────────────────────
    await msg_svc.mark_many_read([msg.id for msg in unread])

    # Commit all changes atomically
    await db.commit()

    log.info(
        "Wake PCA complete",
        extra={
            "provider": wake_response.provider_used,
            "messages_analyzed": wake_response.messages_analyzed,
        },
    )

    return wake_response


@router.post(
    "/reply",
    response_model=PCAReplyResponse,
    summary="Generate reply — AI Call #2: Generate contextual reply",
    description=(
        "Receives user's reply instruction, builds prompt with conversation "
        "context and memory, performs ONE AI API call, saves the draft reply, "
        "and returns the generated reply in the sender's language."
    ),
)
async def generate_reply(
    request: ReplyRequest,
    db: AsyncSession = Depends(get_db),
    msg_svc: MessageService = Depends(get_message_service),
    sender_svc: SenderService = Depends(get_sender_service),
    mem_svc: MemoryService = Depends(get_memory_service),
    reply_svc: ReplyService = Depends(get_reply_service),
    ai_svc: AIService = Depends(get_ai_service),
) -> PCAReplyResponse:
    log.info("POST /pca/reply", extra={"message_id": request.message_id})

    # ── Step 1: Load the target message ──────────────────────────────────────
    message = await msg_svc.get_by_id(request.message_id)

    if message.is_from_user:
        raise InvalidRequestError("Cannot reply to a message sent by the user.")

    # ── Step 2: Load sender profile ───────────────────────────────────────────
    sender = await sender_svc.get_by_id(message.sender_id)
    sender_dict = {
        "name": sender.name,
        "category": sender.category,
        "default_language": sender.default_language,
    }

    # ── Step 3: Conversation history (last 10 messages) ───────────────────────
    history = await msg_svc.get_by_sender(message.sender_id, limit=10)
    history_data = [
        {"text": m.text, "is_from_user": m.is_from_user}
        for m in history
    ]

    # ── Step 4: Sender memory ─────────────────────────────────────────────────
    try:
        mem = await mem_svc.get_by_sender(message.sender_id)
        memory_dict = {
            "summary": mem.summary,
            "key_facts": mem.key_facts,
            "pending_actions": mem.pending_actions,
        }
    except Exception:
        memory_dict = None

    # ── Step 5: Single AI call ────────────────────────────────────────────────
    # (This is the ONLY AI call in the reply flow)
    ai_response = await ai_svc.generate_reply(
        original_message={"text": message.text, "language": message.language},
        sender=sender_dict,
        user_instruction=request.user_instruction,
        conversation_history=history_data,
        memory=memory_dict,
        message_id=message.id,
        user_language="en",
    )

    # ── Step 6: Save draft reply ──────────────────────────────────────────────
    reply_record = await reply_svc.create_draft(
        message_id=message.id,
        generated_reply=ai_response.reply_in_sender_language,
    )

    # ── Step 7: Mark message as replied ──────────────────────────────────────
    await msg_svc.mark_replied(message.id)

    await db.commit()

    # Attach the saved reply ID to the response
    ai_response.reply_id = reply_record.id

    log.info(
        "Reply generated",
        extra={
            "provider": ai_response.provider_used,
            "message_id": message.id,
            "reply_id": reply_record.id,
        },
    )

    return ai_response
