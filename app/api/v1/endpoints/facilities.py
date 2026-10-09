"""Facility management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.deps import get_db
from app.schemas.facility import (
    FacilityResponse,
    FacilityListResponse,
    FacilityNearbyRequest,
)
from app.services.facility_service import FacilityService

router = APIRouter()


@router.get("", response_model=FacilityListResponse)
async def list_facilities(
    city: Optional[str] = Query(None, description="Filter by city"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    verified_only: bool = Query(False, description="Only show verified facilities"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of facilities."""
    skip = (page - 1) * page_size
    facilities, total = await FacilityService.get_facilities(
        db,
        city=city,
        facility_type=facility_type,
        verified_only=verified_only,
        skip=skip,
        limit=page_size,
    )

    return FacilityListResponse(
        facilities=facilities,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/nearby", response_model=List[FacilityResponse])
async def find_nearby_facilities(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(5.0, gt=0, le=100, description="Search radius in km"),
    facility_type: Optional[str] = Query(None, description="Filter by facility type"),
    verified_only: bool = Query(False, description="Only show verified facilities"),
    limit: int = Query(10, gt=0, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """Find nearby facilities based on location."""
    facilities = await FacilityService.get_nearby_facilities(
        db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        facility_type=facility_type,
        verified_only=verified_only,
        limit=limit,
    )

    return facilities


@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    facility_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get facility details by ID."""
    facility = await FacilityService.get_facility_by_id(db, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found",
        )

    return facility