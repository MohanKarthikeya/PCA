"""
Memory router.

GET /memory              - All memory records
GET /memory/{sender_id}  - Memory for a specific sender
"""

from fastapi import APIRouter, Depends

from api.deps import get_memory_service
from schemas.memory import MemoryResponse
from services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("", response_model=list[MemoryResponse], summary="List all memory records")
async def list_memory(svc: MemoryService = Depends(get_memory_service)):
    return await svc.get_all()


@router.get(
    "/{sender_id}",
    response_model=MemoryResponse,
    summary="Get memory for a specific sender",
)
async def get_sender_memory(
    sender_id: str,
    svc: MemoryService = Depends(get_memory_service),
):
    return await svc.get_by_sender(sender_id)
