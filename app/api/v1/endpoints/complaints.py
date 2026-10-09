"""Complaint management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import ComplaintStatus, ComplaintPriority
from app.models.user import User, UserRole
from app.utils.deps import get_db, get_current_user, require_role
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    ComplaintStatusUpdate,
    ComplaintListResponse,
    FeedbackCreate,
    FeedbackResponse,
)
from app.services.complaint_service import ComplaintService

router = APIRouter()


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_create: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new complaint (citizens only)."""
    try:
        complaint = await ComplaintService.create_complaint(
            db, complaint_create, current_user.id
        )
        # Reload with relationships
        complaint = await ComplaintService.get_complaint_by_id(db, complaint.id)
        return complaint
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/mine", response_model=ComplaintListResponse)
async def get_my_complaints(
    status: Optional[ComplaintStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's complaints."""
    skip = (page - 1) * page_size
    complaints, total = await ComplaintService.get_user_complaints(
        db,
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=page_size,
    )

    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("", response_model=ComplaintListResponse)
async def get_all_complaints(
    status: Optional[ComplaintStatus] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    priority: Optional[ComplaintPriority] = Query(None, description="Filter by priority"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_role(UserRole.MUNICIPAL_STAFF, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get all complaints (staff/admin only)."""
    skip = (page - 1) * page_size
    complaints, total = await ComplaintService.get_all_complaints(
        db,
        status=status,
        city=city,
        priority=priority,
        skip=skip,
        limit=page_size,
    )

    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complaint details by ID."""
    complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Check if user has permission to view this complaint
    if (
        current_user.role == UserRole.CITIZEN
        and complaint.reporter_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this complaint",
        )

    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: UUID,
    complaint_update: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update complaint details (owner only while pending/acknowledged)."""
    complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Check ownership
    if complaint.reporter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this complaint",
        )

    # Only allow updates if complaint is pending or acknowledged
    if complaint.status not in [ComplaintStatus.PENDING, ComplaintStatus.ACKNOWLEDGED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update complaints that are pending or acknowledged",
        )

    try:
        # Update complaint fields
        update_data = complaint_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(complaint, field, value)

        await db.commit()
        await db.refresh(complaint)

        # Reload with relationships
        complaint = await ComplaintService.get_complaint_by_id(db, complaint.id)
        return complaint

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete complaint (owner only while pending/acknowledged)."""
    complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Check ownership
    if complaint.reporter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this complaint",
        )

    # Only allow deletion if complaint is pending or acknowledged
    if complaint.status not in [ComplaintStatus.PENDING, ComplaintStatus.ACKNOWLEDGED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete complaints that are pending or acknowledged",
        )

    await db.delete(complaint)
    await db.commit()
    return None


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: UUID,
    status_update: ComplaintStatusUpdate,
    current_user: User = Depends(require_role(UserRole.MUNICIPAL_STAFF, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update complaint status (staff/admin only)."""
    try:
        complaint = await ComplaintService.update_complaint_status(
            db,
            complaint_id=complaint_id,
            new_status=status_update.new_status,
            changed_by=current_user.id,
            remarks=status_update.remarks,
        )

        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found",
            )

        # Reload with relationships
        complaint = await ComplaintService.get_complaint_by_id(db, complaint.id)
        return complaint

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{complaint_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    complaint_id: UUID,
    feedback_create: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a resolved complaint."""
    try:
        feedback = await ComplaintService.create_feedback(
            db,
            complaint_id=complaint_id,
            user_id=current_user.id,
            rating=feedback_create.rating,
            comment=feedback_create.comment,
        )
        return feedback

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )