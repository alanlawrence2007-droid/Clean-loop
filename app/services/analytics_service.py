"""Analytics service for municipal dashboard."""

from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_, extract, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint, ComplaintStatus
from app.models.waste import WasteCategory


class AnalyticsService:
    """Service for analytics and dashboard data."""

    @staticmethod
    async def get_overview(db: AsyncSession) -> Dict[str, Any]:
        """Get analytics overview for dashboard."""
        # Total complaints
        total_result = await db.execute(select(func.count(Complaint.id)))
        total_complaints = total_result.scalar()

        # Status breakdown
        status_query = select(
            Complaint.status,
            func.count(Complaint.id),
        ).group_by(Complaint.status)
        status_result = await db.execute(status_query)
        status_breakdown = [
            {"status": str(row[0]), "count": row[1]} for row in status_result.all()
        ]

        # Category breakdown
        category_query = select(
            WasteCategory.name,
            func.count(Complaint.id),
        ).select_from(
            Complaint.__table__.join(WasteCategory.__table__, isouter=True)
        ).group_by(WasteCategory.name)
        category_result = await db.execute(category_query)
        category_breakdown = [
            {"category_name": row[0] or "Uncategorized", "count": row[1]}
            for row in category_result.all()
        ]

        # Average resolution time (for resolved complaints)
        resolved_query = select(
            func.avg(
                extract("epoch", Complaint.resolved_at - Complaint.created_at) / 3600
            )
        ).where(
            and_(
                Complaint.status == ComplaintStatus.RESOLVED,
                Complaint.resolved_at.is_not(None),
            )
        )
        resolved_result = await db.execute(resolved_query)
        avg_resolution_hours = resolved_result.scalar() or 0.0

        # This month complaints
        now = datetime.now(timezone.utc)
        start_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_last_month = (start_this_month - timedelta(days=1)).replace(day=1)

        this_month_query = select(func.count(Complaint.id)).where(
            Complaint.created_at >= start_this_month
        )
        this_month_result = await db.execute(this_month_query)
        complaints_this_month = this_month_result.scalar()

        last_month_query = select(func.count(Complaint.id)).where(
            and_(
                Complaint.created_at >= start_last_month,
                Complaint.created_at < start_this_month,
            )
        )
        last_month_result = await db.execute(last_month_query)
        complaints_last_month = last_month_result.scalar()

        return {
            "total_complaints": total_complaints,
            "status_breakdown": status_breakdown,
            "category_breakdown": category_breakdown,
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "complaints_this_month": complaints_this_month,
            "complaints_last_month": complaints_last_month,
        }

    @staticmethod
    async def get_hotspots(
        db: AsyncSession, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get complaint hotspots grouped by locality."""
        # Group by city and locality, count complaints
        hotspot_query = select(
            Complaint.city,
            Complaint.locality,
            func.count(Complaint.id).label("complaint_count"),
            func.avg(Complaint.latitude).label("avg_lat"),
            func.avg(Complaint.longitude).label("avg_lon"),
        ).where(
            and_(
                Complaint.city.is_not(None),
                Complaint.locality.is_not(None),
                Complaint.latitude.is_not(None),
                Complaint.longitude.is_not(None),
            )
        ).group_by(
            Complaint.city,
            Complaint.locality,
        ).order_by(
            func.count(Complaint.id).desc()
        ).limit(limit)

        hotspot_result = await db.execute(hotspot_query)

        hotspots = []
        for row in hotspot_result.all():
            city, locality, count, avg_lat, avg_lon = row

            # Get top category for this hotspot
            top_category_query = select(
                WasteCategory.name,
                func.count(Complaint.id),
            ).select_from(
                Complaint.__table__.join(WasteCategory.__table__, isouter=True)
            ).where(
                and_(
                    Complaint.city == city,
                    Complaint.locality == locality,
                )
            ).group_by(WasteCategory.name).order_by(
                func.count(Complaint.id).desc()
            ).limit(1)

            top_category_result = await db.execute(top_category_query)
            top_category_row = top_category_result.first()
            top_category = top_category_row[0] if top_category_row else "Unknown"

            hotspots.append(
                {
                    "latitude": float(avg_lat) if avg_lat else 0.0,
                    "longitude": float(avg_lon) if avg_lon else 0.0,
                    "complaint_count": count,
                    "locality": f"{locality}, {city}",
                    "top_category": top_category,
                }
            )

        return hotspots