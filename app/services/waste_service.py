"""Waste service for waste classification and disposal rules."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.waste import WasteCategory, DisposalRule
from app.schemas.waste import (
    WasteCategoryCreate,
    WasteCategoryUpdate,
    WasteClassificationRequest,
    WasteClassificationResponse,
    DisposalRuleCreate,
    DisposalRuleUpdate,
)


class WasteService:
    """Service for waste management operations."""

    @staticmethod
    async def get_categories(
        db: AsyncSession, active_only: bool = True
    ) -> List[WasteCategory]:
        """Get all waste categories."""
        query = select(WasteCategory)
        if active_only:
            query = query.where(WasteCategory.is_active == True)
        query = query.order_by(WasteCategory.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_category_by_id(
        db: AsyncSession, category_id: UUID
    ) -> Optional[WasteCategory]:
        """Get waste category by ID."""
        result = await db.execute(
            select(WasteCategory).where(WasteCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_slug(
        db: AsyncSession, slug: str
    ) -> Optional[WasteCategory]:
        """Get waste category by slug."""
        result = await db.execute(
            select(WasteCategory).where(WasteCategory.slug == slug)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def classify_waste(
        db: AsyncSession, item_name: str, description: Optional[str] = None
    ) -> dict:
        """
        AI-powered waste classification using keyword matching.

        In production, this would call an ML model. For now, we use
        keyword matching against category names and descriptions.
        """
        # Get all active categories
        categories = await WasteService.get_categories(db, active_only=True)

        if not categories:
            # Fallback if no categories exist
            return {
                "category": None,
                "confidence": 0.0,
                "disposal_instructions": "Please check local disposal guidelines.",
                "tips": None,
            }

        # Simple keyword matching
        item_text = f"{item_name} {description or ''}".lower()

        # Category keywords for matching
        category_keywords = {
            "wet": ["food", "kitchen", "organic", "vegetable", "fruit", "leftover", "peel", "cooked", "raw", "waste", "wet"],
            "dry": ["paper", "plastic", "cardboard", "metal", "glass", "bottle", "can", "wrapper", "packaging", "dry", "recyclable"],
            "e-waste": ["electronic", "phone", "computer", "laptop", "battery", "charger", "cable", "tv", "monitor", "e-waste", "electrical", "gadget"],
            "sanitary": ["diaper", "sanitary", "pad", "tampon", "wipe", "tissue", "hygiene", "medical"],
            "hazardous": ["chemical", "paint", "oil", "pesticide", "cleaner", "acid", "toxic", "hazardous", "poison"],
            "construction": ["concrete", "brick", "cement", "sand", "debris", "construction", "demolition", "rubble"],
            "garden": ["garden", "leaf", "branch", "grass", "plant", "flower", "tree", "yard", "green"],
        }

        best_match = None
        best_score = 0.0

        for category in categories:
            # Check category name
            category_name = category.name.lower()
            score = 0.0

            # Direct name match
            if category_name in item_text:
                score += 0.8

            # Keyword matching
            for key, keywords in category_keywords.items():
                if key in category_name:
                    for keyword in keywords:
                        if keyword in item_text:
                            score += 0.15
                    break

            # Description matching
            if category.description:
                desc_words = category.description.lower().split()
                for word in desc_words:
                    if len(word) > 3 and word in item_text:
                        score += 0.05

            if score > best_score:
                best_score = score
                best_match = category

        # If no match found, default to first category with low confidence
        if best_match is None:
            best_match = categories[0]
            best_score = 0.3

        # Cap confidence at 1.0
        confidence = min(best_score, 1.0)

        # Get disposal rules for the matched category
        rules = await WasteService.get_disposal_rules(db, best_match.id)

        disposal_instructions = rules[0].instructions if rules else "Follow local disposal guidelines."
        tips = rules[0].tips if rules else None

        return {
            "category": best_match,
            "confidence": confidence,
            "disposal_instructions": disposal_instructions,
            "tips": tips,
        }

    @staticmethod
    async def get_disposal_rules(
        db: AsyncSession, category_id: UUID, locality: Optional[str] = None
    ) -> List[DisposalRule]:
        """Get disposal rules for a category, with locality-specific rules first."""
        query = select(DisposalRule).where(
            and_(
                DisposalRule.category_id == category_id,
                DisposalRule.is_active == True,
            )
        )

        # Order by: locality-specific first (if matching), then by priority
        if locality:
            # For simplicity, we'll order by priority desc, then locality nulls last
            query = query.order_by(
                DisposalRule.priority.desc(),
                DisposalRule.locality.is_(None),
                DisposalRule.created_at,
            )
        else:
            query = query.order_by(
                DisposalRule.priority.desc(),
                DisposalRule.locality.is_(None),
                DisposalRule.created_at,
            )

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_category(
        db: AsyncSession, category_create: WasteCategoryCreate
    ) -> WasteCategory:
        """Create a new waste category."""
        category = WasteCategory(**category_create.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: UUID, category_update: WasteCategoryUpdate
    ) -> Optional[WasteCategory]:
        """Update a waste category."""
        category = await WasteService.get_category_by_id(db, category_id)
        if not category:
            return None

        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def create_disposal_rule(
        db: AsyncSession, rule_create: DisposalRuleCreate
    ) -> DisposalRule:
        """Create a new disposal rule."""
        rule = DisposalRule(**rule_create.model_dump())
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def update_disposal_rule(
        db: AsyncSession, rule_id: UUID, rule_update: DisposalRuleUpdate
    ) -> Optional[DisposalRule]:
        """Update a disposal rule."""
        result = await db.execute(
            select(DisposalRule).where(DisposalRule.id == rule_id)
        )
        rule = result.scalar_one_or_none()
        if not rule:
            return None

        update_data = rule_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await db.commit()
        await db.refresh(rule)
        return rule