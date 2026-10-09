"""Complaint API endpoints."""

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.complaint import ComplaintPriority, ComplaintStatus
from app.models.user import User, UserRole
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintResponse,
    ComplaintStatusUpdate,
    ComplaintSyncResponse,
    FeedbackCreate,
    FeedbackResponse,
)
from app.services.complaint_service import ComplaintService
from app.utils.dependencies import get_current_staff, get_current_user

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a complaint",
    description="Submit a new waste management complaint",
)
async def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new complaint.

    - **title**: Complaint title (min 5 characters)
    - **description**: Detailed description (min 10 characters)
    - **client_generated_id**: Optional client-generated ID for offline sync
    - **waste_category_id**: Related waste category
    - **facility_id**: Related facility
    - **address**: Location address
    - **city**: City name
    - **locality**: Locality/area
    - **latitude/longitude**: GPS coordinates
    - **photo_url**: Photo URL
    - **priority**: LOW, MEDIUM, HIGH, or URGENT

    Offline sync: Provide client_generated_id to prevent duplicates.
    """
    complaint, status_msg = await ComplaintService.create(
        db, complaint_data, current_user.id
    )

    if status_msg == "duplicate":
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                "message": "Complaint already exists (duplicate client_generated_id)",
                "id": str(complaint.id),
                "status": "duplicate",
            }
        )

    return complaint


@router.get(
    "/mine",
    response_model=ComplaintListResponse,
    summary="Get my complaints",
    description="Get paginated list of current user's complaints",
)
async def get_my_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's complaints.

    - **page**: Page number
    - **page_size**: Items per page
    - **status**: Filter by status
    """
    complaints, total = await ComplaintService.get_user_complaints(
        db, current_user.id, page, page_size, status_filter
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ComplaintListResponse(
        complaints=[ComplaintResponse.model_validate(c) for c in complaints],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "",
    response_model=ComplaintListResponse,
    summary="Get all complaints (Staff/Admin)",
    description="Get paginated list of all complaints (requires staff or admin role)",
)
async def get_all_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    priority: Optional[ComplaintPriority] = Query(None),
    city: Optional[str] = Query(None),
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all complaints (Staff/Admin only).

    - **page**: Page number
    - **page_size**: Items per page
    - **status**: Filter by status
    - **priority**: Filter by priority
    - **city**: Filter by city
    """
    complaints, total = await ComplaintService.get_all_complaints(
        db, page, page_size, status_filter, priority, city
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ComplaintListResponse(
        complaints=[ComplaintResponse.model_validate(c) for c in complaints],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{complaint_id}",
    response_model=ComplaintDetailResponse,
    summary="Get complaint details",
    description="Get detailed complaint information with status history",
)
async def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complaint by ID with full details.

    Returns:
    - Complaint information
    - Full status history
    - Feedback records
    """
    complaint = await ComplaintService.get_by_id(db, complaint_id)

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )

    # Check access: owner or staff/admin
    if (complaint.reporter_id != current_user.id and
        current_user.role not in [UserRole.MUNICIPAL_STAFF, UserRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return complaint


@router.patch(
    "/{complaint_id}/status",
    response_model=ComplaintResponse,
    summary="Update complaint status (Staff/Admin)",
    description="Update complaint status with history tracking",
)
async def update_complaint_status(
    complaint_id: UUID,
    status_update: ComplaintStatusUpdate,
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """
    Update complaint status (Staff/Admin only).

    - **status**: New status (PENDING, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, CLOSED, REJECTED)
    - **remarks**: Optional remarks for the status change

    Automatically creates status history entry.
    """
    complaint = await ComplaintService.get_by_id(db, complaint_id)

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )

    updated_complaint = await ComplaintService.update_status(
        db, complaint, status_update, current_user.id
    )

    return updated_complaint


@router.post(
    "/{complaint_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback",
    description="Submit feedback for a resolved complaint",
)
async def submit_feedback(
    complaint_id: UUID,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback for a complaint.

    - **rating**: Star rating (1-5)
    - **comment**: Optional comment

    Requirements:
    - Complaint must be resolved or closed
    - User must be the complaint reporter
    """
    complaint = await ComplaintService.get_by_id(db, complaint_id)

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )

    # Check ownership
    if complaint.reporter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the complaint reporter can submit feedback"
        )

    # Check if complaint is resolved
    if complaint.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only submit feedback for resolved or closed complaints"
        )

    feedback = await ComplaintService.add_feedback(
        db, complaint, current_user.id, feedback_data
    )

    return feedback


@router.post(
    "/sync",
    response_model=list[ComplaintSyncResponse],
    summary="Offline sync",
    description="Batch sync complaints from offline mode",
)
async def sync_complaints(
    complaints: list[ComplaintCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync multiple complaints from offline mode.

    Accepts a list of complaints created offline.
    For each complaint:
    - If client_generated_id exists and matches existing complaint, skip
    - Otherwise create new complaint

    Returns sync status for each complaint.
    """
    results = []

    for complaint_data in complaints:
        try:
            complaint, status_msg = await ComplaintService.create(
                db, complaint_data, current_user.id
            )

            results.append(ComplaintSyncResponse(
                id=complaint.id,
                client_generated_id=complaint.client_generated_id,
                status=status_msg,
                message="Complaint synced successfully" if status_msg == "created" else "Duplicate detected",
                created_at=complaint.created_at,
            ))
        except Exception as e:
            results.append(ComplaintSyncResponse(
                id=UUID(int=0),  # Placeholder
                client_generated_id=complaint_data.client_generated_id,
                status="error",
                message=str(e),
                created_at=None,
            ))

    return results
