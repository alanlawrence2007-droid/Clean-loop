"""Waste category and classification API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.waste import (
    DisposalRuleDetailResponse,
    DisposalRuleResponse,
    WasteCategoryResponse,
    WasteClassificationRequest,
    WasteClassificationResponse,
)
from app.services.waste_service import WasteService

router = APIRouter(prefix="/waste", tags=["Waste Management"])


@router.get(
    "/categories",
    response_model=list[WasteCategoryResponse],
    summary="Get all waste categories",
    description="Retrieve all active waste categories for classification",
)
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all waste categories.

    Returns a list of all active waste categories with:
    - Category name and slug
    - Color code for UI
    - Icon identifier
    """
    categories = await WasteService.get_all_categories(db)
    return categories


@router.post(
    "/classify",
    response_model=WasteClassificationResponse,
    summary="Classify waste item",
    description="AI-powered waste classification with disposal instructions",
)
async def classify_waste(
    classification_data: WasteClassificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Classify a waste item and get disposal instructions.

    - **item_name**: Name of the waste item
    - **description**: Optional additional description

    Returns:
    - Identified category
    - Confidence score
    - Disposal instructions
    - Safety tips and warnings
    """
    result = await WasteService.classify_waste(db, classification_data)
    return WasteClassificationResponse(**result)


@router.get(
    "/rules",
    response_model=list[DisposalRuleDetailResponse],
    summary="Get all disposal rules",
    description="Retrieve disposal rules with optional filters",
)
async def get_disposal_rules(
    category_id: Optional[UUID] = Query(None, description="Filter by waste category"),
    locality: Optional[str] = Query(None, description="Filter by locality"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get disposal rules.

    Supports:
    - Filter by category
    - Filter by locality (locality-specific rules prioritized)
    - Returns general rules if no locality specified
    """
    rules = await WasteService.get_disposal_rules(db, category_id, locality)
    return rules


@router.get(
    "/rules/{category_id}",
    response_model=list[DisposalRuleResponse],
    summary="Get disposal rules by category",
    description="Get disposal rules for a specific waste category",
)
async def get_rules_by_category(
    category_id: UUID,
    locality: Optional[str] = Query(None, description="Optional locality filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get disposal rules for a specific category.

    - **category_id**: Waste category UUID
    - **locality**: Optional locality for location-specific rules

    Returns prioritized rules (locality-specific first, then general).
    """
    # Verify category exists
    category = await WasteService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste category not found"
        )

    rules = await WasteService.get_disposal_rules(db, category_id, locality)
    return rules
