"""Complaint service for complaint management."""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.complaint import Complaint, ComplaintPriority, ComplaintStatus, ComplaintStatusHistory, Feedback
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintCreate, ComplaintStatusUpdate, FeedbackCreate


class ComplaintService:
    """Service class for complaint operations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        complaint_data: ComplaintCreate,
        reporter_id: UUID,
    ) -> tuple[Complaint, str]:
        """
        Create a new complaint.

        Args:
            db: Database session
            complaint_data: Complaint creation data
            reporter_id: User ID of the reporter

        Returns:
            Tuple of (created complaint, status message)
        """
        # Check for duplicate if client_generated_id provided
        if complaint_data.client_generated_id:
            existing = await db.execute(
                select(Complaint).where(
                    Complaint.client_generated_id == complaint_data.client_generated_id
                )
            )
            if existing.scalar_one_or_none():
                existing_complaint = existing.scalar_one()
                return existing_complaint, "duplicate"

        # Create complaint
        complaint = Complaint(
            client_generated_id=complaint_data.client_generated_id,
            reporter_id=reporter_id,
            title=complaint_data.title,
            description=complaint_data.description,
            waste_category_id=complaint_data.waste_category_id,
            facility_id=complaint_data.facility_id,
            address=complaint_data.address,
            city=complaint_data.city,
            locality=complaint_data.locality,
            latitude=complaint_data.latitude,
            longitude=complaint_data.longitude,
            photo_url=complaint_data.photo_url,
            priority=complaint_data.priority,
            status=ComplaintStatus.PENDING,
        )

        db.add(complaint)
        await db.flush()

        # Create initial status history
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

        return complaint, "created"

    @staticmethod
    async def get_by_id(db: AsyncSession, complaint_id: UUID) -> Optional[Complaint]:
        """
        Get complaint by ID with relationships.

        Args:
            db: Database session
            complaint_id: Complaint UUID

        Returns:
            Complaint instance with loaded relationships
        """
        result = await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.status_history),
                selectinload(Complaint.feedbacks),
                selectinload(Complaint.waste_category),
                selectinload(Complaint.facility),
            )
            .where(Complaint.id == complaint_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_complaints(
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
        status: Optional[ComplaintStatus] = None,
    ) -> tuple[list[Complaint], int]:
        """
        Get paginated complaints for a user.

        Args:
            db: Database session
            user_id: User UUID
            page: Page number
            page_size: Items per page
            status: Filter by status

        Returns:
            Tuple of (complaints list, total count)
        """
        query = select(Complaint).where(Complaint.reporter_id == user_id)

        if status:
            query = query.where(Complaint.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Get paginated results
        query = query.order_by(desc(Complaint.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        complaints = list(result.scalars().all())

        return complaints, total

    @staticmethod
    async def get_all_complaints(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        status: Optional[ComplaintStatus] = None,
        priority: Optional[ComplaintPriority] = None,
        city: Optional[str] = None,
    ) -> tuple[list[Complaint], int]:
        """
        Get paginated complaints for staff/admin.

        Args:
            db: Database session
            page: Page number
            page_size: Items per page
            status: Filter by status
            priority: Filter by priority
            city: Filter by city

        Returns:
            Tuple of (complaints list, total count)
        """
        query = select(Complaint).options(selectinload(Complaint.reporter))

        if status:
            query = query.where(Complaint.status == status)
        if priority:
            query = query.where(Complaint.priority == priority)
        if city:
            query = query.where(Complaint.city.ilike(f"%{city}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Get paginated results
        query = query.order_by(desc(Complaint.priority), desc(Complaint.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        complaints = list(result.scalars().all())

        return complaints, total

    @staticmethod
    async def update_status(
        db: AsyncSession,
        complaint: Complaint,
        status_update: ComplaintStatusUpdate,
        changed_by: UUID,
    ) -> Complaint:
        """
        Update complaint status with history tracking.

        Args:
            db: Database session
            complaint: Complaint instance
            status_update: Status update data
            changed_by: User ID making the change

        Returns:
            Updated complaint instance
        """
        previous_status = complaint.status
        new_status = status_update.status

        # Update complaint status
        complaint.status = new_status

        # Set resolution details if resolved
        if new_status == ComplaintStatus.RESOLVED:
            complaint.resolved_at = datetime.now(timezone.utc)
            complaint.resolved_by = changed_by
            if status_update.remarks:
                complaint.resolution_notes = status_update.remarks

        # Create status history entry
        status_history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            changed_by=changed_by,
            previous_status=previous_status,
            new_status=new_status,
            remarks=status_update.remarks,
        )
        db.add(status_history)

        await db.commit()
        await db.refresh(complaint)

        return complaint

    @staticmethod
    async def add_feedback(
        db: AsyncSession,
        complaint: Complaint,
        user_id: UUID,
        feedback_data: FeedbackCreate,
    ) -> Feedback:
        """
        Add feedback to a resolved complaint.

        Args:
            db: Database session
            complaint: Complaint instance
            user_id: User ID providing feedback
            feedback_data: Feedback data

        Returns:
            Created feedback instance
        """
        feedback = Feedback(
            complaint_id=complaint.id,
            user_id=user_id,
            rating=feedback_data.rating,
            comment=feedback_data.comment,
        )

        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)

        return feedback


    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
