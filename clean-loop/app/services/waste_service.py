"""Waste service for categories and disposal rules."""

import json
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.waste import DisposalRule, WasteCategory
from app.schemas.waste import DisposalRuleCreate, WasteCategoryCreate, WasteClassificationRequest


class WasteService:
    """Service class for waste operations."""

    @staticmethod
    async def get_all_categories(db: AsyncSession) -> list[WasteCategory]:
        """
        Get all active waste categories.

        Args:
            db: Database session

        Returns:
            List of waste categories
        """
        result = await db.execute(
            select(WasteCategory)
            .where(WasteCategory.is_active == True)
            .order_by(WasteCategory.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: UUID) -> Optional[WasteCategory]:
        """
        Get waste category by ID.

        Args:
            db: Database session
            category_id: Category UUID

        Returns:
            WasteCategory instance or None
        """
        result = await db.execute(
            select(WasteCategory).where(WasteCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_slug(db: AsyncSession, slug: str) -> Optional[WasteCategory]:
        """
        Get waste category by slug.

        Args:
            db: Database session
            slug: Category slug

        Returns:
            WasteCategory instance or None
        """
        result = await db.execute(
            select(WasteCategory).where(WasteCategory.slug == slug)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(
        db: AsyncSession,
        category_data: WasteCategoryCreate,
    ) -> WasteCategory:
        """
        Create a new waste category.

        Args:
            db: Database session
            category_data: Category creation data

        Returns:
            Created category instance
        """
        category = WasteCategory(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            color_code=category_data.color_code,
            icon=category_data.icon,
        )

        db.add(category)
        await db.commit()
        await db.refresh(category)

        return category

    @staticmethod
    async def get_disposal_rules(
        db: AsyncSession,
        category_id: Optional[UUID] = None,
        locality: Optional[str] = None,
    ) -> list[DisposalRule]:
        """
        Get disposal rules with optional filters.

        Args:
            db: Database session
            category_id: Filter by category
            locality: Filter by locality

        Returns:
            List of disposal rules
        """
        query = select(DisposalRule).options(
            selectinload(DisposalRule.category)
        ).where(DisposalRule.is_active == True)

        if category_id:
            query = query.where(DisposalRule.category_id == category_id)

        if locality:
            # Prefer locality-specific rules
            query = query.where(
                (DisposalRule.locality == locality) |
                (DisposalRule.locality.is_(None))
            )
        else:
            # General rules only
            query = query.where(DisposalRule.locality.is_(None))

        query = query.order_by(DisposalRule.priority.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_disposal_rule_by_id(db: AsyncSession, rule_id: UUID) -> Optional[DisposalRule]:
        """
        Get disposal rule by ID with category.

        Args:
            db: Database session
            rule_id: Rule UUID

        Returns:
            DisposalRule instance with loaded category
        """
        result = await db.execute(
            select(DisposalRule)
            .options(selectinload(DisposalRule.category))
            .where(DisposalRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_disposal_rule(
        db: AsyncSession,
        rule_data: DisposalRuleCreate,
    ) -> DisposalRule:
        """
        Create a new disposal rule.

        Args:
            db: Database session
            rule_data: Rule creation data

        Returns:
            Created disposal rule instance
        """
        rule = DisposalRule(
            category_id=rule_data.category_id,
            title=rule_data.title,
            description=rule_data.description,
            instructions=rule_data.instructions,
            locality=rule_data.locality,
            pickup_schedule=rule_data.pickup_schedule,
            pickup_time=rule_data.pickup_time,
            tips=rule_data.tips,
            warnings=rule_data.warnings,
            priority=rule_data.priority,
        )

        db.add(rule)
        await db.commit()
        await db.refresh(rule)

        return rule

    @staticmethod
    async def classify_waste(
        db: AsyncSession,
        classification_data: WasteClassificationRequest,
    ) -> dict:
        """
        Classify waste item and provide disposal instructions.

        This is a rule-based classification. In production, this would
        integrate with an AI model for more accurate classification.

        Args:
            db: Database session
            classification_data: Classification request data

        Returns:
            Classification result with category and instructions
        """
        item_name = classification_data.item_name.lower()
        description = (classification_data.description or "").lower()
        combined = f"{item_name} {description}"

        # Define classification rules
        classification_rules = {
            "wet": {
                "keywords": ["food", "vegetable", "fruit", "meat", "fish", "dairy", "cooked", "leftover", "organic", "garden", "leaves", "flower"],
                "category_slug": "wet-waste",
            },
            "dry": {
                "keywords": ["paper", "cardboard", "plastic", "glass", "metal", "can", "bottle", "box", "newspaper", "magazine"],
                "category_slug": "dry-waste",
            },
            "e-waste": {
                "keywords": ["electronic", "battery", "phone", "computer", "laptop", "charger", "cable", "tv", "appliance"],
                "category_slug": "e-waste",
            },
            "hazardous": {
                "keywords": ["chemical", "paint", "oil", "pesticide", "medicine", "syringe", "needle", "asbestos", "toxic"],
                "category_slug": "hazardous-waste",
            },
            "sanitary": {
                "keywords": ["diaper", "sanitary", "pad", "tissue", "bandage", "mask", "glove", "medical"],
                "category_slug": "sanitary-waste",
            },
        }

        # Determine category based on keywords
        matched_category_slug = "dry-waste"  # Default
        confidence = 0.5
        matched_keywords = []

        for category_type, rules in classification_rules.items():
            keywords = rules["keywords"]
            matches = [kw for kw in keywords if kw in combined]

            if matches:
                match_score = len(matches) / len(keywords)
                if match_score > confidence:
                    confidence = match_score
                    matched_category_slug = rules["category_slug"]
                    matched_keywords = matches

        # Get category from database
        category = await WasteService.get_category_by_slug(db, matched_category_slug)

        # Get disposal rules for category
        rules = await WasteService.get_disposal_rules(
            db,
            category_id=category.id if category else None,
            locality=None,
        )

        result = {
            "category": category.name if category else "Unknown",
            "category_id": category.id if category else None,
            "confidence": min(confidence * 1.5, 0.95),  # Adjust confidence
        }

        if rules:
            rule = rules[0]  # Get first matching rule
            result["disposal_instructions"] = rule.instructions
            result["tips"] = rule.tips
            result["warnings"] = rule.warnings

        return result
