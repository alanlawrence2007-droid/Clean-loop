"""Waste category and disposal rule schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WasteCategoryBase(BaseModel):
    """Base waste category schema."""

    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)


class WasteCategoryCreate(WasteCategoryBase):
    """Schema for creating a waste category."""

    pass


class WasteCategoryUpdate(BaseModel):
    """Schema for updating a waste category."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class WasteCategoryResponse(WasteCategoryBase):
    """Waste category response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DisposalRuleBase(BaseModel):
    """Base disposal rule schema."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    instructions: str
    locality: Optional[str] = Field(None, max_length=255)
    pickup_schedule: Optional[str] = Field(None, max_length=255)
    pickup_time: Optional[str] = Field(None, max_length=100)
    tips: Optional[str] = None
    warnings: Optional[str] = None
    priority: int = 0


class DisposalRuleCreate(DisposalRuleBase):
    """Schema for creating a disposal rule."""

    category_id: UUID


class DisposalRuleUpdate(BaseModel):
    """Schema for updating a disposal rule."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    locality: Optional[str] = Field(None, max_length=255)
    pickup_schedule: Optional[str] = None
    pickup_time: Optional[str] = None
    tips: Optional[str] = None
    warnings: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class DisposalRuleResponse(DisposalRuleBase):
    """Disposal rule response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class WasteClassificationRequest(BaseModel):
    """Request schema for AI waste classification."""

    item_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class WasteClassificationResponse(BaseModel):
    """Response schema for AI waste classification."""

    item_name: str
    category: WasteCategoryResponse
    confidence: float = Field(..., ge=0.0, le=1.0)
    disposal_instructions: str
    tips: Optional[str] = None
    rules: List[DisposalRuleResponse] = []
