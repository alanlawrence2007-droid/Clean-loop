"""Complaint schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.complaint import ComplaintPriority, ComplaintStatus


# Status History Schemas
class ComplaintStatusHistoryBase(BaseModel):
    """Base schema for status history."""
    new_status: ComplaintStatus
    remarks: str | None = None


class ComplaintStatusHistoryResponse(ComplaintStatusHistoryBase):
    """Schema for status history response."""
    id: UUID
    complaint_id: UUID
    changed_by: UUID
    previous_status: ComplaintStatus | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintStatusHistoryDetail(ComplaintStatusHistoryResponse):
    """Schema for status history with user details."""
    changed_by_name: str | None = Field(None, description="Name of user who changed status")


# Feedback Schemas
class FeedbackBase(BaseModel):
    """Base schema for feedback."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: str | None = Field(None, max_length=1000)


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""
    pass


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    id: UUID
    complaint_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Complaint Schemas
class ComplaintBase(BaseModel):
    """Base schema for complaint."""
    title: str = Field(..., min_length=5, max_length=255, description="Complaint title")
    description: str = Field(..., min_length=10, description="Detailed description")
    address: str | None = Field(None, description="Location address")
    city: str | None = Field(None, max_length=100, description="City name")
    locality: str | None = Field(None, max_length=255, description="Locality/area")


class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint."""
    client_generated_id: UUID | None = Field(
        None,
        description="Client-generated ID for offline sync (prevents duplicates)"
    )
    waste_category_id: UUID | None = Field(None, description="Waste category ID")
    facility_id: UUID | None = Field(None, description="Related facility ID")
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    photo_url: str | None = Field(None, max_length=500, description="Photo URL")
    priority: ComplaintPriority = ComplaintPriority.MEDIUM


class ComplaintUpdate(BaseModel):
    """Schema for updating complaint status."""
    status: ComplaintPriority | None = None
    priority: ComplaintPriority | None = None


class ComplaintStatusUpdate(BaseModel):
    """Schema for updating complaint status (staff/admin only)."""
    status: ComplaintStatus = Field(..., description="New status")
    remarks: str | None = Field(None, max_length=1000, description="Optional remarks for status change")


class ComplaintResponse(ComplaintBase):
    """Schema for complaint response."""
    id: UUID
    client_generated_id: UUID | None = None
    reporter_id: UUID
    waste_category_id: UUID | None = None
    facility_id: UUID | None = None
    status: ComplaintStatus
    priority: ComplaintPriority
    latitude: float | None = None
    longitude: float | None = None
    photo_url: str | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    resolved_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplaintDetailResponse(ComplaintResponse):
    """Schema for complaint with full details."""
    status_history: list[ComplaintStatusHistoryResponse] = []
    feedbacks: list[FeedbackResponse] = []


class ComplaintListResponse(BaseModel):
    """Schema for paginated complaint list."""
    complaints: list[ComplaintResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ComplaintSyncResponse(BaseModel):
    """Schema for offline sync response."""
    id: UUID
    client_generated_id: UUID | None
    status: str = Field(..., description="Sync status: 'created', 'duplicate', 'error'")
    message: str
    created_at: datetime | None = None
