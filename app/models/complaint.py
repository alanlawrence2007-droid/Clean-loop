"""Complaint model with status history and feedback."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.facility import Facility
    from app.models.user import User
    from app.models.waste import WasteCategory


class ComplaintStatus(str, enum.Enum):
    """Complaint status enumeration."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ComplaintPriority(str, enum.Enum):
    """Complaint priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Complaint(Base):
    """
    Complaint model for waste management issues.

    Supports offline-first architecture with client-generated IDs.
    Tracks full status history for audit trail.
    """

    __tablename__ = "complaints"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Client-generated ID for offline sync (prevents duplicates)
    client_generated_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
        index=True,
    )

    # Reporter
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Complaint details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Waste categorization
    waste_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("waste_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Location
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    locality: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # PostGIS location
    location: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # Legacy lat/long
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Assigned facility
    facility_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status and priority
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus),
        default=ComplaintStatus.PENDING,
        nullable=False,
        index=True,
    )
    priority: Mapped[ComplaintPriority] = mapped_column(
        Enum(ComplaintPriority),
        default=ComplaintPriority.MEDIUM,
        nullable=False,
        index=True,
    )

    # Image support
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Resolution details
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="complaints",
        foreign_keys=[reporter_id],
    )
    waste_category: Mapped[Optional["WasteCategory"]] = relationship(
        "WasteCategory",
        back_populates="complaints",
    )
    facility: Mapped[Optional["Facility"]] = relationship(
        "Facility",
        back_populates="complaints",
    )
    status_history: Mapped[List["ComplaintStatusHistory"]] = relationship(
        "ComplaintStatusHistory",
        back_populates="complaint",
        cascade="all, delete-orphan",
        order_by="desc(ComplaintStatusHistory.created_at)",
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="complaint",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Complaint {self.title} ({self.status})>"


class ComplaintStatusHistory(Base):
    """
    Full status history for complaints.

    Tracks every status change with timestamp, user, and remarks.
    Provides complete audit trail for compliance.
    """

    __tablename__ = "complaint_status_history"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign keys
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status change
    previous_status: Mapped[Optional[ComplaintStatus]] = mapped_column(
        Enum(ComplaintStatus),
        nullable=True,
    )
    new_status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus),
        nullable=False,
    )

    # Additional info
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="status_history",
    )
    changed_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="status_histories",
    )

    def __repr__(self) -> str:
        return f"<StatusHistory {self.complaint_id}: {self.new_status}>"


class Feedback(Base):
    """
    User feedback on resolved complaints.

    Allows citizens to rate and comment on complaint resolution.
    """

    __tablename__ = "feedbacks"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign keys
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Feedback details
    rating: Mapped[int] = mapped_column(nullable=False)  # 1-5 stars
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="feedbacks",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="feedbacks",
    )

    def __repr__(self) -> str:
        return f"<Feedback {self.rating} stars for {self.complaint_id}>"