"""Facility schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FacilityBase(BaseModel):
    """Base schema for facility."""
    name: str = Field(..., min_length=1, max_length=255)
    facility_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    state: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str = "India"
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=500)
    operating_hours: str | None = None
    accepted_waste_types: str | None = None


class FacilityCreate(FacilityBase):
    """Schema for creating a facility."""
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)


class FacilityUpdate(BaseModel):
    """Schema for updating a facility."""
    name: str | None = Field(None, min_length=1, max_length=255)
    facility_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    operating_hours: str | None = None
    accepted_waste_types: str | None = None
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    is_active: bool | None = None


class FacilityResponse(FacilityBase):
    """Schema for facility response."""
    id: UUID
    latitude: float | None = None
    longitude: float | None = None
    is_verified: bool
    verified_at: datetime | None = None
    last_updated: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FacilityNearbyRequest(BaseModel):
    """Schema for nearby facilities query."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    radius_km: float = Field(5.0, ge=0.1, le=100.0, description="Search radius in kilometers")
    facility_type: str | None = Field(None, description="Filter by facility type")


class FacilityWithDistance(FacilityResponse):
    """Schema for facility with distance from user location."""
    distance_km: float = Field(..., description="Distance from the search point in kilometers")


class FacilityVerificationRequest(BaseModel):
    """Schema for verifying a facility."""
    is_verified: bool = Field(..., description="Verification status")
