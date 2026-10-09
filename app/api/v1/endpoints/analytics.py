"""Analytics endpoints for municipal dashboard."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.utils.deps import get_db, get_current_user, require_role
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    HotspotListResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    current_user: User = Depends(require_role(UserRole.MUNICIPAL_STAFF, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics overview for dashboard (staff/admin only)."""
    overview_data = await AnalyticsService.get_overview(db)
    return AnalyticsOverviewResponse(**overview_data)


@router.get("/hotspots", response_model=HotspotListResponse)
async def get_complaint_hotspots(
    limit: int = 10,
    current_user: User = Depends(require_role(UserRole.MUNICIPAL_STAFF, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get complaint hotspots for dashboard (staff/admin only)."""
    hotspots = await AnalyticsService.get_hotspots(db, limit=limit)
    return HotspotListResponse(hotspots=hotspots)