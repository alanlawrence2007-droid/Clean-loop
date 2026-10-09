"""Complaint schemas for complaint management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.complaint import ComplaintStatus, ComplaintPriority
from app.schemas.user import UserResponse
from app.schemas.waste import WasteCategoryResponse
from app.schemas.facility import FacilityResponse


class ComplaintBase(BaseModel):
    """Base complaint schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    waste_category_id: Optional[UUID] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    locality: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    facility_id: Optional[UUID] = None
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    photo_url: Optional[str] = Field(None, max_length=500)


class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint."""

    client_generated_id: Optional[UUID] = None


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    waste_category_id: Optional[UUID] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    locality: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    facility_id: Optional[UUID] = None
    priority: Optional[ComplaintPriority] = None
    photo_url: Optional[str] = Field(None, max_length=500)


class ComplaintStatusUpdate(BaseModel):
    """Schema for updating complaint status."""

    new_status: ComplaintStatus
    remarks: Optional[str] = None


class ComplaintStatusHistoryResponse(BaseModel):
    """Complaint status history response schema."""

    id: UUID
    complaint_id: UUID
    changed_by: UUID
    previous_status: Optional[ComplaintStatus] = None
    new_status: ComplaintStatus
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""

    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response schema."""

    id: UUID
    complaint_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintResponse(ComplaintBase):
    """Complaint response schema with relationships."""

    id: UUID
    client_generated_id: Optional[UUID] = None
    reporter_id: UUID
    status: ComplaintStatus
    priority: ComplaintPriority
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    # Relationships
    reporter: UserResponse
    waste_category: Optional[WasteCategoryResponse] = None
    facility: Optional[FacilityResponse] = None
    status_history: List[ComplaintStatusHistoryResponse] = []
    feedbacks: List[FeedbackResponse] = []

    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    """Paginated complaint list response."""

    complaints: List[ComplaintResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True


class ComplaintSyncRequest(BaseModel):
    """Schema for offline sync request."""

    complaints: List[ComplaintCreate]


class ComplaintSyncResponse(BaseModel):
    """Schema for offline sync response."""

    synced: List[str]
    duplicates: List[str]
    errors: List[dict]