"""Facility schemas for waste management facilities."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FacilityBase(BaseModel):
    """Base facility schema."""

    name: str = Field(..., max_length=255)
    facility_type: str = Field(..., max_length=100)
    description: Optional[str] = None
    address: str
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="India", max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    operating_hours: Optional[str] = None
    accepted_waste_types: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class FacilityCreate(FacilityBase):
    """Schema for creating a facility."""
    pass


class FacilityUpdate(BaseModel):
    """Schema for updating a facility."""

    name: Optional[str] = Field(None, max_length=255)
    facility_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    operating_hours: Optional[str] = None
    accepted_waste_types: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None


class FacilityResponse(FacilityBase):
    """Facility response schema."""

    id: UUID
    is_verified: bool
    verified_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityNearbyRequest(BaseModel):
    """Request schema for nearby facilities search."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=100)
    facility_type: Optional[str] = None
    verified_only: bool = False
    limit: int = Field(default=10, gt=0, le=50)


class FacilityListResponse(BaseModel):
    """Paginated facility list response."""

    facilities: List[FacilityResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True