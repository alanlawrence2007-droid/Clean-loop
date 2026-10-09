"""Facility service for waste management facilities."""

import math
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityUpdate


class FacilityService:
    """Service class for facility operations."""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        facility_type: Optional[str] = None,
        city: Optional[str] = None,
        is_verified: Optional[bool] = None,
    ) -> tuple[list[Facility], int]:
        """
        Get paginated facilities with optional filters.

        Args:
            db: Database session
            page: Page number
            page_size: Items per page
            facility_type: Filter by type
            city: Filter by city
            is_verified: Filter by verification status

        Returns:
            Tuple of (facilities list, total count)
        """
        query = select(Facility).where(Facility.is_active == True)

        if facility_type:
            query = query.where(Facility.facility_type == facility_type)
        if city:
            query = query.where(Facility.city.ilike(f"%{city}%"))
        if is_verified is not None:
            query = query.where(Facility.is_verified == is_verified)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Get paginated results
        query = query.order_by(desc(Facility.is_verified), desc(Facility.last_updated))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        facilities = list(result.scalars().all())

        return facilities, total

    @staticmethod
    async def get_by_id(db: AsyncSession, facility_id: UUID) -> Optional[Facility]:
        """
        Get facility by ID.

        Args:
            db: Database session
            facility_id: Facility UUID

        Returns:
            Facility instance or None
        """
        result = await db.execute(
            select(Facility).where(Facility.id == facility_id, Facility.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_nearby(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        facility_type: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Get facilities within radius of a point.

        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            facility_type: Filter by type
            limit: Maximum results

        Returns:
            List of facilities with distance information
        """
        # Query all active facilities with coordinates
        query = select(Facility).where(
            Facility.is_active == True,
            Facility.latitude.isnot(None),
            Facility.longitude.isnot(None),
        )

        if facility_type:
            query = query.where(Facility.facility_type == facility_type)

        result = await db.execute(query)
        facilities = result.scalars().all()

        # Calculate distances and filter
        nearby = []
        for facility in facilities:
            if facility.latitude and facility.longitude:
                distance = FacilityService.calculate_distance(
                    latitude, longitude,
                    facility.latitude, facility.longitude
                )

                if distance <= radius_km:
                    nearby.append({
                        "facility": facility,
                        "distance_km": round(distance, 2),
                    })

        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])

        return nearby[:limit]

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    async def create(db: AsyncSession, facility_data: FacilityCreate) -> Facility:
        """
        Create a new facility.

        Args:
            db: Database session
            facility_data: Facility creation data

        Returns:
            Created facility instance
        """
        facility = Facility(
            name=facility_data.name,
            facility_type=facility_data.facility_type,
            description=facility_data.description,
            address=facility_data.address,
            city=facility_data.city,
            state=facility_data.state,
            postal_code=facility_data.postal_code,
            country=facility_data.country,
            phone=facility_data.phone,
            email=facility_data.email,
            website=facility_data.website,
            operating_hours=facility_data.operating_hours,
            accepted_waste_types=facility_data.accepted_waste_types,
            latitude=facility_data.latitude,
            longitude=facility_data.longitude,
            is_verified=False,
            is_active=True,
        )

        db.add(facility)
        await db.commit()
        await db.refresh(facility)

        return facility

    @staticmethod
    async def update(
        db: AsyncSession,
        facility: Facility,
        update_data: FacilityUpdate,
    ) -> Facility:
        """
        Update facility information.

        Args:
            db: Database session
            facility: Facility instance
            update_data: Update data

        Returns:
            Updated facility instance
        """
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            if hasattr(facility, key) and value is not None:
                setattr(facility, key, value)

        await db.commit()
        await db.refresh(facility)

        return facility

    @staticmethod
    async def verify(
        db: AsyncSession,
        facility: Facility,
        verifier_id: UUID,
    ) -> Facility:
        """
        Verify a facility.

        Args:
            db: Database session
            facility: Facility instance
            verifier_id: User ID of verifier

        Returns:
            Updated facility instance
        """
        facility.is_verified = True
        facility.verified_at = datetime.now(timezone.utc)
        facility.verified_by = verifier_id

        await db.commit()
        await db.refresh(facility)

        return facility


# Import datetime for verify method
from datetime import datetime, timezone
