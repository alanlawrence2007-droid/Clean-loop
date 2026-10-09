"""Waste management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.deps import get_db
from app.schemas.waste import (
    WasteCategoryResponse,
    WasteClassificationRequest,
    WasteClassificationResponse,
    DisposalRuleResponse,
)
from app.services.waste_service import WasteService

router = APIRouter()


@router.get("/categories", response_model=List[WasteCategoryResponse])
async def get_categories(
    active_only: bool = Query(True, description="Only return active categories"),
    db: AsyncSession = Depends(get_db),
):
    """Get all waste categories."""
    categories = await WasteService.get_categories(db, active_only=active_only)
    return categories


@router.post("/classify", response_model=WasteClassificationResponse)
async def classify_waste(
    classification_request: WasteClassificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Classify a waste item using AI."""
    result = await WasteService.classify_waste(
        db,
        classification_request.item_name,
        classification_request.description,
    )

    if not result["category"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No waste categories available for classification",
        )

    return WasteClassificationResponse(
        item_name=classification_request.item_name,
        category=result["category"],
        confidence=result["confidence"],
        disposal_instructions=result["disposal_instructions"],
        tips=result["tips"],
        rules=[],  # Will be populated separately if needed
    )


@router.get("/rules", response_model=List[DisposalRuleResponse])
async def get_disposal_rules(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    locality: Optional[str] = Query(None, description="Filter by locality"),
    db: AsyncSession = Depends(get_db),
):
    """Get disposal rules, optionally filtered by category and locality."""
    if category_id:
        rules = await WasteService.get_disposal_rules(db, category_id, locality)
    else:
        # Get all rules (need to implement this in service)
        from sqlalchemy import select
        from app.models.waste import DisposalRule
        result = await db.execute(select(DisposalRule).where(DisposalRule.is_active == True))
        rules = list(result.scalars().all())

    return rules


@router.get("/rules/{category_id}", response_model=List[DisposalRuleResponse])
async def get_rules_by_category(
    category_id: UUID,
    locality: Optional[str] = Query(None, description="Filter by locality"),
    db: AsyncSession = Depends(get_db),
):
    """Get disposal rules for a specific category."""
    # Verify category exists
    category = await WasteService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    rules = await WasteService.get_disposal_rules(db, category_id, locality)
    return rules