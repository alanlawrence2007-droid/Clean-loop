"""Analytics API endpoints for municipal dashboard."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsOverview, HotspotsListResponse
from app.services.analytics_service import AnalyticsService
from app.utils.dependencies import get_current_staff

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverview,
    summary="Get analytics overview",
    description="Get comprehensive analytics for municipal dashboard (Staff/Admin only)",
)
async def get_analytics_overview(
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive analytics overview.

    Returns:
    - Total complaints by status
    - Average resolution time
    - Facility statistics
    - Time-based metrics
    - Top waste categories
    - Resolution rate

    Requires municipal_staff or admin role.
    """
    overview = await AnalyticsService.get_overview(db)
    return overview


@router.get(
    "/hotspots",
    response_model=HotspotsListResponse,
    summary="Get complaint hotspots",
    description="Identify complaint hotspots for resource allocation (Staff/Admin only)",
)
async def get_hotspots(
    limit: int = Query(10, ge=1, le=50, description="Maximum hotspots to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complaint hotspots.

    Identifies areas with high complaint density:
    - Locality-based grouping
    - Severity score calculation
    - Recent activity tracking
    - Top categories per hotspot

    Use for:
    - Resource allocation
    - Targeted interventions
    - Performance monitoring

    Requires municipal_staff or admin role.
    """
    hotspots = await AnalyticsService.get_hotspots(db, limit, city)

    return HotspotsListResponse(
        hotspots=hotspots,
        total=len(hotspots),
    )
