"""Analytics service for municipal dashboard."""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint, ComplaintStatus
from app.models.facility import Facility
from app.models.waste import WasteCategory
from app.schemas.analytics import AnalyticsOverview, HotspotResponse


class AnalyticsService:
    """Service class for analytics operations."""

    @staticmethod
    async def get_overview(db: AsyncSession) -> AnalyticsOverview:
        """
        Get comprehensive analytics overview.

        Args:
            db: Database session

        Returns:
            Analytics overview data
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Total complaints by status
        status_counts = {}
        for status in ComplaintStatus:
            result = await db.execute(
                select(func.count()).where(Complaint.status == status)
            )
            status_counts[status.value] = result.scalar_one()

        total_complaints = sum(status_counts.values())

        # Facility counts
        total_facilities_result = await db.execute(
            select(func.count()).where(Facility.is_active == True)
        )
        total_facilities = total_facilities_result.scalar_one()

        verified_facilities_result = await db.execute(
            select(func.count()).where(
                Facility.is_active == True,
                Facility.is_verified == True,
            )
        )
        verified_facilities = verified_facilities_result.scalar_one()

        # Time-based counts
        week_count_result = await db.execute(
            select(func.count()).where(Complaint.created_at >= week_ago)
        )
        complaints_this_week = week_count_result.scalar_one()

        month_count_result = await db.execute(
            select(func.count()).where(Complaint.created_at >= month_ago)
        )
        complaints_this_month = month_count_result.scalar_one()

        # Average resolution time
        resolved_complaints_result = await db.execute(
            select(Complaint).where(
                Complaint.status == ComplaintStatus.RESOLVED,
                Complaint.resolved_at.isnot(None),
            )
        )
        resolved_complaints = resolved_complaints_result.scalars().all()

        avg_resolution_hours = None
        if resolved_complaints:
            total_hours = 0
            for c in resolved_complaints:
                if c.created_at and c.resolved_at:
                    delta = c.resolved_at - c.created_at
                    total_hours += delta.total_seconds() / 3600
            avg_resolution_hours = total_hours / len(resolved_complaints)

        # Top categories
        category_counts_result = await db.execute(
            select(
                WasteCategory.name,
                func.count(Complaint.id).label('count')
            )
            .join(Complaint, Complaint.waste_category_id == WasteCategory.id, isouter=True)
            .group_by(WasteCategory.id, WasteCategory.name)
            .order_by(desc('count'))
            .limit(5)
        )
        top_categories = [
            {"name": row.name, "count": row.count}
            for row in category_counts_result.all()
        ]

        # Resolution rate
        resolved_count = status_counts.get(ComplaintStatus.RESOLVED.value, 0)
        closed_count = status_counts.get(ComplaintStatus.CLOSED.value, 0)
        resolution_rate = ((resolved_count + closed_count) / total_complaints * 100) if total_complaints > 0 else 0.0

        return AnalyticsOverview(
            total_complaints=total_complaints,
            pending_complaints=status_counts.get(ComplaintStatus.PENDING.value, 0),
            in_progress_complaints=status_counts.get(ComplaintStatus.IN_PROGRESS.value, 0),
            resolved_complaints=resolved_count,
            closed_complaints=closed_count,
            rejected_complaints=status_counts.get(ComplaintStatus.REJECTED.value, 0),
            average_resolution_time_hours=round(avg_resolution_hours, 2) if avg_resolution_hours else None,
            total_facilities=total_facilities,
            verified_facilities=verified_facilities,
            unverified_facilities=total_facilities - verified_facilities,
            complaints_this_week=complaints_this_week,
            complaints_this_month=complaints_this_month,
            top_categories=top_categories,
            resolution_rate=round(resolution_rate, 2),
        )

    @staticmethod
    async def get_hotspots(
        db: AsyncSession,
        limit: int = 10,
        city: Optional[str] = None,
    ) -> list[HotspotResponse]:
        """
        Get complaint hotspots based on locality.

        Args:
            db: Database session
            limit: Maximum number of hotspots
            city: Filter by city

        Returns:
            List of hotspot data
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # Build query
        query = (
            select(
                Complaint.locality,
                Complaint.city,
                Complaint.latitude,
                Complaint.longitude,
                func.count(Complaint.id).label('total_count'),
            )
            .where(Complaint.locality.isnot(None))
            .group_by(
                Complaint.locality,
                Complaint.city,
                Complaint.latitude,
                Complaint.longitude,
            )
            .order_by(desc('total_count'))
        )

        if city:
            query = query.where(Complaint.city.ilike(f"%{city}%"))

        result = await db.execute(query.limit(limit))
        rows = result.all()

        hotspots = []
        for row in rows:
            # Get recent complaints for this locality
            recent_result = await db.execute(
                select(func.count()).where(
                    Complaint.locality == row.locality,
                    Complaint.created_at >= week_ago,
                )
            )
            recent_count = recent_result.scalar_one()

            # Calculate severity score (0-100)
            # Based on total count and recent activity
            severity = min(100, (row.total_count * 2) + (recent_count * 5))

            # Get top categories for this locality
            cat_result = await db.execute(
                select(WasteCategory.name)
                .join(Complaint, Complaint.waste_category_id == WasteCategory.id)
                .where(Complaint.locality == row.locality)
                .group_by(WasteCategory.name)
                .order_by(desc(func.count(Complaint.id)))
                .limit(3)
            )
            top_cats = [r.name for r in cat_result.all()]

            hotspots.append(HotspotResponse(
                locality=row.locality or "Unknown",
                city=row.city,
                latitude=row.latitude,
                longitude=row.longitude,
                complaint_count=row.total_count,
                recent_complaints=recent_count,
                severity_score=round(severity, 2),
                top_categories=top_cats,
            ))

        return hotspots
