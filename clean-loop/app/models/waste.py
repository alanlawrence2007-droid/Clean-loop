"""Waste category and disposal rule models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class WasteCategory(Base):
    """
    Waste category for classification.

    Categories include: Wet, Dry, E-waste, Sanitary, Hazardous, etc.
    Each category has specific disposal rules and guidelines.
    """

    __tablename__ = "waste_categories"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Category details
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon identifier

    # Metadata
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
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
    disposal_rules: Mapped[List["DisposalRule"]] = relationship(
        "DisposalRule",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    complaints: Mapped[List["Complaint"]] = relationship(
        "Complaint",
        back_populates="waste_category",
    )

    def __repr__(self) -> str:
        return f"<WasteCategory {self.name}>"


class DisposalRule(Base):
    """
    Disposal rules for waste categories.

    Supports locality-specific rules for different regions.
    General rules apply when no locality-specific rule exists.
    """

    __tablename__ = "disposal_rules"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign key to category
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("waste_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Rule details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    # Locality support (optional for general rules)
    locality: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Disposal details
    pickup_schedule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pickup_time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Additional info
    tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warnings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Priority for locality matching
    priority: Mapped[int] = mapped_column(default=0, nullable=False)

    # Metadata
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
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
    category: Mapped["WasteCategory"] = relationship(
        "WasteCategory",
        back_populates="disposal_rules",
    )

    def __repr__(self) -> str:
        return f"<DisposalRule {self.title}>"
