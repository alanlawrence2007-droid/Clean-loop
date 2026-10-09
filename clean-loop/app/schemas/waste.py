"""Waste category and disposal rule schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WasteCategoryBase(BaseModel):
    """Base schema for waste category."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    color_code: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    icon: str | None = Field(None, max_length=50)


class WasteCategoryCreate(WasteCategoryBase):
    """Schema for creating waste category."""
    pass


class WasteCategoryResponse(WasteCategoryBase):
    """Schema for waste category response."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WasteClassificationRequest(BaseModel):
    """Schema for AI waste classification request."""
    item_name: str = Field(..., min_length=1, max_length=255, description="Name of the waste item")
    description: str | None = Field(None, description="Additional description of the item")


class WasteClassificationResponse(BaseModel):
    """Schema for waste classification response."""
    category: str = Field(..., description="Identified waste category")
    category_id: UUID | None = None
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    disposal_instructions: str | None = None
    tips: str | None = None
    warnings: str | None = None


class DisposalRuleBase(BaseModel):
    """Base schema for disposal rule."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    instructions: str = Field(..., description="Disposal instructions")
    locality: str | None = Field(None, max_length=255, description="Specific locality for this rule")
    pickup_schedule: str | None = None
    pickup_time: str | None = None
    tips: str | None = None
    warnings: str | None = None


class DisposalRuleCreate(DisposalRuleBase):
    """Schema for creating disposal rule."""
    category_id: UUID
    priority: int = 0


class DisposalRuleResponse(DisposalRuleBase):
    """Schema for disposal rule response."""
    id: UUID
    category_id: UUID
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DisposalRuleDetailResponse(DisposalRuleResponse):
    """Schema for disposal rule with category details."""
    category: WasteCategoryResponse | None = None

    model_config = {"from_attributes": True}
