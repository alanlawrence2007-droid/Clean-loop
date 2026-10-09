"""Facility service for waste management facilities."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityUpdate


class FacilityService:
    """Service for facility operations."""

    @staticmethod
    async def get_facilities(
        db: AsyncSession,
        city: Optional[str] = None,
        facility_type: Optional[str] = None,
        verified_only: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Facility], int]:
        """Get paginated list of facilities with filters."""
        query = select(Facility).where(Facility.is_active == True)

        if city:
            query = query.where(Facility.city.ilike(f"%{city}%"))
        if facility_type:
            query = query.where(Facility.facility_type == facility_type)
        if verified_only:
            query = query.where(Facility.is_verified == True)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Facility.name).offset(skip).limit(limit)
        result = await db.execute(query)
        facilities = list(result.scalars().all())

        return facilities, total

    @staticmethod
    async def get_facility_by_id(db: AsyncSession, facility_id: UUID) -> Optional[Facility]:
        """Get facility by ID."""
        result = await db.execute(
            select(Facility).where(Facility.id == facility_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_nearby_facilities(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        facility_type: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 10,
    ) -> List[Facility]:
        """
        Find nearby facilities using PostGIS if available,
        otherwise use Haversine formula on lat/long columns.
        """
        query = select(Facility).where(
            and_(
                Facility.is_active == True,
                Facility.latitude.is_not(None),
                Facility.longitude.is_not(None),
            )
        )

        if facility_type:
            query = query.where(Facility.facility_type == facility_type)
        if verified_only:
            query = query.where(Facility.is_verified == True)

        # Use Haversine formula for distance calculation
        # Distance = 6371 * acos(cos(lat1)*cos(lat2)*cos(lon2-lon1) + sin(lat1)*sin(lat2))
        # where 6371 is Earth radius in km
        from sqlalchemy import text

        haversine_formula = text(
            """
            6371 * acos(
                cos(radians(:lat1)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(:lon1)) +
                sin(radians(:lat1)) * sin(radians(latitude))
            )
            """
        )

        query = query.add_columns(
            haversine_formula.label("distance_km")
        ).where(
            haversine_formula <= radius_km
        ).order_by(
            "distance_km"
        ).limit(limit)

        result = await db.execute(query, {"lat1": latitude, "lon1": longitude})
        facilities = [row[0] for row in result.all()]

        return facilities

    @staticmethod
    async def create_facility(
        db: AsyncSession, facility_create: FacilityCreate
    ) -> Facility:
        """Create a new facility."""
        facility = Facility(**facility_create.model_dump())
        db.add(facility)
        await db.commit()
        await db.refresh(facility)
        return facility

    @staticmethod
    async def update_facility(
        db: AsyncSession, facility_id: UUID, facility_update: FacilityUpdate
    ) -> Optional[Facility]:
        """Update a facility."""
        facility = await FacilityService.get_facility_by_id(db, facility_id)
        if not facility:
            return None

        update_data = facility_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(facility, field, value)

        await db.commit()
        await db.refresh(facility)
        return facility

    @staticmethod
    async def verify_facility(
        db: AsyncSession, facility_id: UUID, verified_by: UUID
    ) -> Optional[Facility]:
        """Verify a facility (staff/admin only)."""
        from datetime import datetime, timezone

        facility = await FacilityService.get_facility_by_id(db, facility_id)
        if not facility:
            return None

        facility.is_verified = True
        facility.verified_at = datetime.now(timezone.utc)
        facility.verified_by = verified_by

        await db.commit()
        await db.refresh(facility)
        return facility