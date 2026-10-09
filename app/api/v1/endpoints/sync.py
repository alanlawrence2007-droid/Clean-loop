"""Offline sync endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.deps import get_db, get_current_user
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintSyncRequest,
    ComplaintSyncResponse,
)
from app.services.complaint_service import ComplaintService

router = APIRouter()


@router.post("/complaints", response_model=ComplaintSyncResponse)
async def sync_complaints(
    sync_request: ComplaintSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync offline complaints with duplicate prevention."""
    result = await ComplaintService.sync_complaints(
        db=db,
        complaints=sync_request.complaints,
        reporter_id=current_user.id,
    )
    return ComplaintSyncResponse(**result)