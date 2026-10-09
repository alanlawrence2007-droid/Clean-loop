"""Analytics schemas for municipal dashboard."""

from typing import List
from pydantic import BaseModel


class StatusCount(BaseModel):
    """Status count for analytics."""

    status: str
    count: int


class CategoryCount(BaseModel):
    """Category count for analytics."""

    category_name: str
    count: int


class AnalyticsOverviewResponse(BaseModel):
    """Analytics overview response for dashboard."""

    total_complaints: int
    status_breakdown: List[StatusCount]
    category_breakdown: List[CategoryCount]
    avg_resolution_hours: float
    complaints_this_month: int
    complaints_last_month: int


class HotspotResponse(BaseModel):
    """Complaint hotspot response."""

    latitude: float
    longitude: float
    complaint_count: int
    locality: str
    top_category: str


class HotspotListResponse(BaseModel):
    """Hotspot list response."""

    hotspots: List[HotspotResponse]