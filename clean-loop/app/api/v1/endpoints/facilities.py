"""Facility API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.facility import (
    FacilityNearbyRequest,
    FacilityResponse,
    FacilityWithDistance,
)
from app.services.facility_service import FacilityService
from app.utils.dependencies import get_current_admin, get_current_staff, get_current_user

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get(
    "",
    response_model=dict,
    summary="Get all facilities",
    description="Retrieve paginated list of waste management facilities",
)
async def get_facilities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all facilities with pagination and filters.

    - **page**: Page number (starts from 1)
    - **page_size**: Items per page (max 100)
    - **facility_type**: Filter by type (e.g., recycling_center, e_waste_center)
    - **city**: Filter by city name
    - **is_verified**: Filter verified/unverified facilities
    """
    facilities, total = await FacilityService.get_all(
        db, page, page_size, facility_type, city, is_verified
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "facilities": [FacilityResponse.model_validate(f) for f in facilities],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get(
    "/nearby",
    response_model=list[FacilityWithDistance],
    summary="Find nearby facilities",
    description="Find facilities within a radius of your location",
)
async def get_nearby_facilities(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Your latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Your longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=100.0, description="Search radius in km"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Find facilities near your location.

    - **latitude**: Your current latitude
    - **longitude**: Your current longitude
    - **radius_km**: Search radius (default 5km, max 100km)
    - **facility_type**: Optional filter by facility type

    Returns facilities sorted by distance.
    """
    nearby = await FacilityService.get_nearby(
        db, latitude, longitude, radius_km, facility_type
    )

    return [
        FacilityWithDistance(
            **FacilityResponse.model_validate(item["facility"]).model_dump(),
            distance_km=item["distance_km"],
        )
        for item in nearby
    ]


@router.get(
    "/{facility_id}",
    response_model=FacilityResponse,
    summary="Get facility by ID",
    description="Get detailed information about a specific facility",
)
async def get_facility(
    facility_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get facility details by ID.

    Returns:
    - Facility information
    - Verification status
    - Operating hours
    - Accepted waste types
    """
    facility = await FacilityService.get_by_id(db, facility_id)

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    return facility
