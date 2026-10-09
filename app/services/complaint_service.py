"""Complaint service for complaint management."""

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import (
    Complaint,
    ComplaintStatus,
    ComplaintPriority,
    ComplaintStatusHistory,
    Feedback,
)
from app.models.user import User
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintStatusUpdate,
    FeedbackCreate,
)


class ComplaintService:
    """Service for complaint operations."""

    @staticmethod
    async def create_complaint(
        db: AsyncSession, complaint_create: ComplaintCreate, reporter_id: UUID
    ) -> Complaint:
        """Create a new complaint with initial status history."""
        # Check for duplicate client_generated_id
        if complaint_create.client_generated_id:
            existing = await db.execute(
                select(Complaint).where(
                    Complaint.client_generated_id == complaint_create.client_generated_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Complaint with this client_generated_id already exists")

        # Create complaint
        complaint_data = complaint_create.model_dump(exclude={"client_generated_id"})
        complaint = Complaint(
            **complaint_data,
            reporter_id=reporter_id,
            client_generated_id=complaint_create.client_generated_id,
        )
        db.add(complaint)
        await db.flush()

        # Create initial status history entry
        status_history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            changed_by=reporter_id,
            previous_status=None,
            new_status=ComplaintStatus.PENDING,
            remarks="Complaint submitted",
        )
        db.add(status_history)

        await db.commit()
        await db.refresh(complaint)
        return complaint

    @staticmethod
    async def get_complaint_by_id(
        db: AsyncSession, complaint_id: UUID
    ) -> Optional[Complaint]:
        """Get complaint by ID with relationships loaded."""
        result = await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.reporter),
                selectinload(Complaint.waste_category),
                selectinload(Complaint.facility),
                selectinload(Complaint.status_history).selectinload(
                    ComplaintStatusHistory.changed_by_user
                ),
                selectinload(Complaint.feedbacks).selectinload(Feedback.user),
            )
            .where(Complaint.id == complaint_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_complaints(
        db: AsyncSession,
        user_id: UUID,
        status: Optional[ComplaintStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Complaint], int]:
        """Get complaints for a specific user."""
        query = select(Complaint).where(Complaint.reporter_id == user_id)

        if status:
            query = query.where(Complaint.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results with relationships
        query = (
            query.options(
                selectinload(Complaint.waste_category),
                selectinload(Complaint.facility),
                selectinload(Complaint.status_history),
                selectinload(Complaint.feedbacks),
            )
            .order_by(desc(Complaint.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        complaints = list(result.scalars().all())

        return complaints, total

    @staticmethod
    async def get_all_complaints(
        db: AsyncSession,
        status: Optional[ComplaintStatus] = None,
        city: Optional[str] = None,
        priority: Optional[ComplaintPriority] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Complaint], int]:
        """Get all complaints (staff/admin) with filters."""
        query = select(Complaint)

        if status:
            query = query.where(Complaint.status == status)
        if city:
            query = query.where(Complaint.city.ilike(f"%{city}%"))
        if priority:
            query = query.where(Complaint.priority == priority)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results with relationships
        query = (
            query.options(
                selectinload(Complaint.reporter),
                selectinload(Complaint.waste_category),
                selectinload(Complaint.facility),
                selectinload(Complaint.status_history),
                selectinload(Complaint.feedbacks),
            )
            .order_by(desc(Complaint.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        complaints = list(result.scalars().all())

        return complaints, total

    @staticmethod
    async def update_complaint_status(
        db: AsyncSession,
        complaint_id: UUID,
        new_status: ComplaintStatus,
        changed_by: UUID,
        remarks: Optional[str] = None,
    ) -> Optional[Complaint]:
        """Update complaint status and create history entry."""
        complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
        if not complaint:
            return None

        previous_status = complaint.status
        complaint.status = new_status

        # Set resolution fields if resolved
        if new_status == ComplaintStatus.RESOLVED:
            complaint.resolved_at = datetime.now(timezone.utc)
            complaint.resolved_by = changed_by

        # Create status history entry
        status_history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            changed_by=changed_by,
            previous_status=previous_status,
            new_status=new_status,
            remarks=remarks,
        )
        db.add(status_history)

        await db.commit()
        await db.refresh(complaint)
        return complaint

    @staticmethod
    async def sync_complaints(
        db: AsyncSession, complaints: List[ComplaintCreate], reporter_id: UUID
    ) -> Dict[str, Any]:
        """Sync offline complaints with duplicate prevention."""
        synced = []
        duplicates = []
        errors = []

        for complaint_create in complaints:
            try:
                # Check for duplicate by client_generated_id
                if complaint_create.client_generated_id:
                    existing = await db.execute(
                        select(Complaint).where(
                            and_(
                                Complaint.client_generated_id
                                == complaint_create.client_generated_id,
                                Complaint.reporter_id == reporter_id,
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        duplicates.append(str(complaint_create.client_generated_id))
                        continue

                # Create complaint
                complaint = await ComplaintService.create_complaint(
                    db, complaint_create, reporter_id
                )
                synced.append(str(complaint.id))

            except Exception as e:
                errors.append(
                    {
                        "client_generated_id": str(complaint_create.client_generated_id)
                        if complaint_create.client_generated_id
                        else None,
                        "error": str(e),
                    }
                )

        return {
            "synced": synced,
            "duplicates": duplicates,
            "errors": errors,
        }

    @staticmethod
    async def create_feedback(
        db: AsyncSession,
        complaint_id: UUID,
        user_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Create feedback for a resolved complaint."""
        # Verify complaint exists and is resolved
        complaint = await ComplaintService.get_complaint_by_id(db, complaint_id)
        if not complaint:
            raise ValueError("Complaint not found")

        if complaint.status != ComplaintStatus.RESOLVED:
            raise ValueError("Can only submit feedback for resolved complaints")

        # Check if user already submitted feedback
        existing = await db.execute(
            select(Feedback).where(
                and_(
                    Feedback.complaint_id == complaint_id,
                    Feedback.user_id == user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Feedback already submitted for this complaint")

        feedback = Feedback(
            complaint_id=complaint_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback