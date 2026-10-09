"""Analytics schemas for municipal dashboard."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsOverview(BaseModel):
    """Schema for analytics overview."""
    total_complaints: int = Field(..., description="Total number of complaints")
    pending_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    closed_complaints: int
    rejected_complaints: int

    average_resolution_time_hours: float | None = Field(
        None, description="Average time to resolve complaints in hours"
    )

    total_facilities: int
    verified_facilities: int
    unverified_facilities: int

    complaints_this_week: int
    complaints_this_month: int

    top_categories: list[dict[str, int | str]] = Field(
        default_factory=list,
        description="Top waste categories by complaint count"
    )

    resolution_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of resolved complaints"
    )


class HotspotResponse(BaseModel):
    """Schema for complaint hotspot."""
    locality: str
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    complaint_count: int
    recent_complaints: int = Field(..., description="Complaints in last 7 days")
    severity_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Calculated severity based on count and recency"
    )
    top_categories: list[str] = Field(
        default_factory=list,
        description="Most common waste categories in this area"
    )


class HotspotsListResponse(BaseModel):
    """Schema for list of hotspots."""
    hotspots: list[HotspotResponse]
    total: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryStatsResponse(BaseModel):
    """Schema for category-wise statistics."""
    category_id: UUID
    category_name: str
    complaint_count: int
    percentage: float
    resolved_count: int
    pending_count: int


class TimeSeriesDataPoint(BaseModel):
    """Schema for a single time series data point."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int


class ComplaintTrendResponse(BaseModel):
    """Schema for complaint trend over time."""
    data: list[TimeSeriesDataPoint]
    period: str = Field(..., description="Period: 'daily', 'weekly', 'monthly'")
