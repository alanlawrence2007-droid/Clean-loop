"""Facility model for waste management facilities."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class FacilityType(str):
    """Facility type constants."""
    RECYCLING_CENTER = "recycling_center"
    WASTE_COLLECTION_POINT = "waste_collection_point"
    COMPOSTING_FACILITY = "composting_facility"
    HAZARDOUS_WASTE_DEPOT = "hazardous_waste_depot"
    E_WASTE_CENTER = "e_waste_center"
    LANDFILL = "landfill"
    TRANSFER_STATION = "transfer_station"


class Facility(Base):
    """
    Waste management facility model.

    Supports location-based queries with PostGIS.
    Facilities can be verified by municipal staff for authenticity.
    """

    __tablename__ = "facilities"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Facility details
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    facility_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Contact information
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)

    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Operating hours
    operating_hours: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Accepted waste types (JSON array stored as text)
    accepted_waste_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location (PostGIS geography point)
    location: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # Legacy lat/long for convenience
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Verification status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Last update tracking
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    complaints: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        back_populates="facility",
    )

    def __repr__(self) -> str:
        return f"<Facility {self.name} ({self.facility_type})>"
