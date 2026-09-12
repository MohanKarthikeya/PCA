"""
Senders router.

GET    /senders       - List all senders
POST   /senders       - Create a sender
DELETE /senders/{id}  - Delete a sender
"""

from fastapi import APIRouter, Depends, status

from api.deps import get_sender_service
from schemas.sender import SenderCreate, SenderResponse
from services.sender_service import SenderService

router = APIRouter(prefix="/senders", tags=["Senders"])


@router.get("", response_model=list[SenderResponse], summary="List all senders")
async def list_senders(svc: SenderService = Depends(get_sender_service)):
    return await svc.get_all()


@router.post(
    "",
    response_model=SenderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a sender",
)
async def create_sender(
    data: SenderCreate,
    svc: SenderService = Depends(get_sender_service),
):
    return await svc.create(data)


@router.delete(
    "/{sender_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sender",
)
async def delete_sender(
    sender_id: str,
    svc: SenderService = Depends(get_sender_service),
):
    await svc.delete(sender_id)
