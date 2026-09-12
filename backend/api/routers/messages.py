"""
Messages router.

GET  /messages           - All messages (paginated)
GET  /messages/unread    - Unread messages (optional sender_id filter)
POST /messages           - Create a new message
PUT  /messages/{id}/read - Mark message as read
PUT  /messages/{id}/reply - Mark message as replied
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from api.deps import get_message_service
from schemas.message import MessageCreate, MessageResponse
from services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])
log = logging.getLogger("pca.api.messages")


@router.get("", response_model=list[MessageResponse], summary="List all messages")
async def list_messages(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    svc: MessageService = Depends(get_message_service),
):
    log.info("GET /messages", extra={"path": str(request.url)})
    return await svc.get_all(limit=limit, offset=offset)


@router.get(
    "/unread",
    response_model=list[MessageResponse],
    summary="List unread messages",
)
async def list_unread_messages(
    sender_id: str | None = Query(default=None, description="Filter by sender"),
    svc: MessageService = Depends(get_message_service),
):
    return await svc.get_unread(sender_id=sender_id)


@router.post("", response_model=MessageResponse, status_code=201, summary="Create message")
async def create_message(
    data: MessageCreate,
    svc: MessageService = Depends(get_message_service),
):
    return await svc.create(data)


@router.put(
    "/{message_id}/read",
    response_model=MessageResponse,
    summary="Mark message as read",
)
async def mark_read(
    message_id: str,
    svc: MessageService = Depends(get_message_service),
):
    return await svc.mark_read(message_id)


@router.put(
    "/{message_id}/reply",
    response_model=MessageResponse,
    summary="Mark message as replied",
)
async def mark_replied(
    message_id: str,
    svc: MessageService = Depends(get_message_service),
):
    return await svc.mark_replied(message_id)
