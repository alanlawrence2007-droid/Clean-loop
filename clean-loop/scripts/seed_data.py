"""Database seed script for Clean Loop.

Run with: python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.complaint import Complaint, ComplaintPriority, ComplaintStatus
from app.models.facility import Facility
from app.models.user import User, UserRole
from app.models.waste import DisposalRule, WasteCategory


async def seed_database() -> None:
    """Seed the database with initial data."""
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Seeding database...")

        # ========== USERS ==========
        print("\n👤 Creating users...")

        users_data = [
            {
                "email": "admin@cleanloop.gov",
                "full_name": "System Administrator",
                "password": "admin12345",
                "role": UserRole.ADMIN,
                "phone": "+91-9876543210",
            },
            {
                "email": "staff1@cleanloop.gov",
                "full_name": "Rajesh Kumar",
                "password": "staff12345",
                "role": UserRole.MUNICIPAL_STAFF,
                "phone": "+91-9876543211",
            },
            {
                "email": "staff2@cleanloop.gov",
                "full_name": "Priya Sharma",
                "password": "staff12345",
                "role": UserRole.MUNICIPAL_STAFF,
                "phone": "+91-9876543212",
            },
            {
                "email": "citizen1@example.com",
                "full_name": "Amit Patel",
                "password": "citizen12345",
                "role": UserRole.CITIZEN,
                "phone": "+91-9876543213",
            },
            {
                "email": "citizen2@example.com",
                "full_name": "Sneha Reddy",
                "password": "citizen12345",
                "role": UserRole.CITIZEN,
                "phone": "+91-9876543214",
            },
        ]

        users = []
        for user_data in users_data:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                user = User(
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    phone=user_data["phone"],
                    is_active=True,
                )
                session.add(user)
                await session.flush()
                users.append(user)
                print(f"  ✓ Created user: {user.email} ({user.role.value})")
            else:
                users.append(existing)
                print(f"  → User exists: {existing.email}")

        await session.commit()

        # ========== WASTE CATEGORIES ==========
        print("\n🗑️ Creating waste categories...")

        categories_data = [
            {
                "name": "Wet Waste",
                "slug": "wet-waste",
                "description": "Biodegradable waste including food scraps, garden waste, and organic materials",
                "color_code": "#4CAF50",
                "icon": "wet-waste",
            },
            {
                "name": "Dry Waste",
                "slug": "dry-waste",
                "description": "Recyclable waste including paper, plastic, glass, metal, and cardboard",
                "color_code": "#2196F3",
                "icon": "dry-waste",
            },
            {
                "name": "E-Waste",
                "slug": "e-waste",
                "description": "Electronic waste including phones, computers, batteries, and electronic appliances",
                "color_code": "#FF9800",
                "icon": "e-waste",
            },
            {
                "name": "Hazardous Waste",
                "slug": "hazardous-waste",
                "description": "Dangerous waste including chemicals, paints, oils, pesticides, and medical waste",
                "color_code": "#F44336",
                "icon": "hazardous",
            },
            {
                "name": "Sanitary Waste",
                "slug": "sanitary-waste",
                "description": "Personal hygiene waste including diapers, sanitary napkins, and tissues",
                "color_code": "#9C27B0",
                "icon": "sanitary",
            },
            {
                "name": "Construction Waste",
                "slug": "construction-waste",
                "description": "Building and demolition debris including concrete, bricks, and tiles",
                "color_code": "#795548",
                "icon": "construction",
            },
            {
                "name": "Biomedical Waste",
                "slug": "biomedical-waste",
                "description": "Medical facility waste including syringes, bandages, and expired medicines",
                "color_code": "#E91E63",
                "icon": "biomedical",
            },
        ]

        categories = []
        for cat_data in categories_data:
            result = await session.execute(
                select(WasteCategory).where(WasteCategory.slug == cat_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                category = WasteCategory(**cat_data)
                session.add(category)
                await session.flush()
                categories.append(category)
                print(f"  ✓ Created category: {category.name}")
            else:
                categories.append(existing)
                print(f"  → Category exists: {existing.name}")

        await session.commit()

        # ========== DISPOSAL RULES ==========
        print("\n📋 Creating disposal rules...")

        disposal_rules_data = [
            # Wet Waste Rules
            {
                "category_slug": "wet-waste",
                "title": "General Wet Waste Disposal",
                "description": "Standard guidelines for disposing wet waste",
                "instructions": "Separate wet waste in green bins. Drain excess liquid. Wrap in newspaper if possible. Do not mix with plastic.",
                "pickup_schedule": "Daily",
                "pickup_time": "7:00 AM - 9:00 AM",
                "tips": "Use compostable bags. Consider home composting for garden waste.",
                "warnings": "Never mix wet waste with hazardous materials. Avoid disposing cooking oil in wet waste.",
            },
            {
                "category_slug": "wet-waste",
                "title": "Indiranagar Wet Waste Rules",
                "description": "Locality-specific wet waste disposal for Indiranagar",
                "instructions": "Use only green color-coded bins. Separate vegetable waste from cooked food. Composting available at community center.",
                "locality": "Indiranagar",
                "pickup_schedule": "Daily except Sunday",
                "pickup_time": "6:30 AM - 8:30 AM",
                "priority": 10,
            },
            # Dry Waste Rules
            {
                "category_slug": "dry-waste",
                "title": "General Dry Waste Disposal",
                "description": "Standard guidelines for disposing dry recyclable waste",
                "instructions": "Rinse containers before disposal. Flatten cardboard boxes. Separate paper, plastic, glass, and metal. Use blue bins.",
                "pickup_schedule": "Monday, Wednesday, Friday",
                "pickup_time": "8:00 AM - 10:00 AM",
                "tips": "Remove caps from bottles. Crush plastic bottles to save space. Store paper in dry place.",
                "warnings": "Remove all food residue. Do not mix with wet waste.",
            },
            # E-Waste Rules
            {
                "category_slug": "e-waste",
                "title": "Electronic Waste Disposal",
                "description": "Proper disposal of electronic items",
                "instructions": "Do not dispose in regular bins. Take to designated e-waste collection centers. Remove batteries before disposal. Data wipe devices.",
                "pickup_schedule": "Second Saturday of each month",
                "pickup_time": "9:00 AM - 5:00 PM",
                "tips": "Check manufacturer take-back programs. Many retailers offer e-waste collection.",
                "warnings": "Never burn electronic items. Batteries can explode in fire. Mercury in screens is toxic.",
            },
            # Hazardous Waste Rules
            {
                "category_slug": "hazardous-waste",
                "title": "Hazardous Waste Disposal",
                "description": "Safe disposal of dangerous materials",
                "instructions": "Keep in original containers if possible. Never mix different chemicals. Take to hazardous waste collection points. Label all containers clearly.",
                "pickup_schedule": "Quarterly collection drives",
                "tips": "Use gloves when handling. Store away from children. Check expiry dates.",
                "warnings": "HIGHLY DANGEROUS - Never pour down drains. Do not burn. Keep away from heat sources.",
            },
            # Sanitary Waste Rules
            {
                "category_slug": "sanitary-waste",
                "title": "Sanitary Waste Disposal",
                "description": "Proper disposal of hygiene products",
                "instructions": "Wrap in newspaper or special sanitary bags. Dispose in designated red bins. Never flush down toilet.",
                "pickup_schedule": "Daily",
                "pickup_time": "7:00 AM - 9:00 AM",
                "tips": "Use biodegradable sanitary products when possible. Keep separate from other waste.",
                "warnings": "Do not flush sanitary products - causes drain blockages.",
            },
        ]

        for rule_data in disposal_rules_data:
            category_slug = rule_data.pop("category_slug")
            result = await session.execute(
                select(WasteCategory).where(WasteCategory.slug == category_slug)
            )
            category = result.scalar_one_or_none()

            if category:
                rule = DisposalRule(
                    category_id=category.id,
                    **rule_data,
                )
                session.add(rule)
                print(f"  ✓ Created rule: {rule.title}")

        await session.commit()

        # ========== FACILITIES ==========
        print("\n🏢 Creating facilities...")

        facilities_data = [
            {
                "name": "Koramangala Recycling Center",
                "facility_type": "recycling_center",
                "description": "Main recycling facility accepting paper, plastic, glass, and metal waste. E-waste collection on weekends.",
                "address": "123, 5th Block, Koramangala Main Road",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560034",
                "country": "India",
                "phone": "+91-80-25551234",
                "email": "koramangala@cleanloop.gov",
                "website": "https://cleanloop.gov/koramangala",
                "operating_hours": "Mon-Sat: 8:00 AM - 6:00 PM, Sun: 9:00 AM - 1:00 PM",
                "accepted_waste_types": '["paper", "plastic", "glass", "metal", "e-waste"]',
                "latitude": 12.9352,
                "longitude": 77.6245,
                "is_verified": True,
            },
            {
                "name": "Indiranagar Waste Collection Point",
                "facility_type": "waste_collection_point",
                "description": "Neighborhood waste collection point for all types of waste. Segregation mandatory.",
                "address": "45, 12th Main, Indiranagar",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560038",
                "country": "India",
                "phone": "+91-80-25253456",
                "operating_hours": "Daily: 6:00 AM - 10:00 AM, 4:00 PM - 8:00 PM",
                "accepted_waste_types": '["wet-waste", "dry-waste", "sanitary"]',
                "latitude": 12.9784,
                "longitude": 77.6408,
                "is_verified": True,
            },
            {
                "name": "Electronic City E-Waste Center",
                "facility_type": "e_waste_center",
                "description": "Specialized facility for electronic waste disposal and recycling. Data destruction services available.",
                "address": "Phase 1, Electronic City Industrial Area",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560100",
                "country": "India",
                "phone": "+91-80-28521234",
                "email": "ewaste@cleanloop.gov",
                "website": "https://cleanloop.gov/ewaste",
                "operating_hours": "Mon-Fri: 9:00 AM - 5:00 PM, Sat: 9:00 AM - 1:00 PM",
                "accepted_waste_types": '["e-waste", "batteries", "electronics"]',
                "latitude": 12.8399,
                "longitude": 77.6770,
                "is_verified": True,
            },
            {
                "name": "Jayanagar Composting Facility",
                "facility_type": "composting_facility",
                "description": "Large-scale composting facility for organic waste. Community composting programs available.",
                "address": "78, 4th Block, Jayanagar",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560041",
                "country": "India",
                "phone": "+91-80-26547890",
                "operating_hours": "Daily: 6:00 AM - 12:00 PM",
                "accepted_waste_types": '["wet-waste", "garden-waste", "organic"]',
                "latitude": 12.9250,
                "longitude": 77.5938,
                "is_verified": True,
            },
            {
                "name": "Peenya Hazardous Waste Depot",
                "facility_type": "hazardous_waste_depot",
                "description": "Authorized facility for hazardous waste disposal. Chemical, industrial, and medical waste accepted with proper documentation.",
                "address": "Plot 45, Industrial Area Phase 2, Peenya",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560058",
                "country": "India",
                "phone": "+91-80-28367890",
                "email": "hazardous@cleanloop.gov",
                "operating_hours": "Mon-Fri: 9:00 AM - 4:00 PM (Appointment Required)",
                "accepted_waste_types": '["hazardous", "chemical", "medical-waste", "industrial"]',
                "latitude": 13.0236,
                "longitude": 77.5127,
                "is_verified": True,
            },
            {
                "name": "Whitefield Transfer Station",
                "facility_type": "transfer_station",
                "description": "Waste transfer and segregation station serving Whitefield and ITPL areas.",
                "address": "ITPL Main Road, Whitefield",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560066",
                "country": "India",
                "phone": "+91-80-28452345",
                "operating_hours": "24/7 (Drop-off: 6:00 AM - 9:00 PM)",
                "accepted_waste_types": '["wet-waste", "dry-waste", "construction-waste"]',
                "latitude": 12.9698,
                "longitude": 77.7500,
                "is_verified": True,
            },
            {
                "name": "HSR Layout Collection Point",
                "facility_type": "waste_collection_point",
                "description": "Community waste collection center with segregation awareness programs.",
                "address": "Sector 2, HSR Layout",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560102",
                "country": "India",
                "phone": "+91-80-25721234",
                "operating_hours": "Daily: 6:00 AM - 10:00 AM",
                "accepted_waste_types": '["wet-waste", "dry-waste"]',
                "latitude": 12.9116,
                "longitude": 77.6389,
                "is_verified": False,
            },
            {
                "name": "MG Road Central Collection",
                "facility_type": "waste_collection_point",
                "description": "Central waste collection point serving commercial and residential areas.",
                "address": "MG Road, Near Metro Station",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India",
                "phone": "+91-80-25554567",
                "operating_hours": "Daily: 6:00 AM - 11:00 AM, 4:00 PM - 8:00 PM",
                "accepted_waste_types": '["wet-waste", "dry-waste", "sanitary"]',
                "latitude": 12.9756,
                "longitude": 77.6064,
                "is_verified": True,
            },
            {
                "name": "BTM Layout Segregation Center",
                "facility_type": "waste_collection_point",
                "description": "Modern waste segregation center with educational facility.",
                "address": "2nd Stage, BTM Layout",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560076",
                "country": "India",
                "phone": "+91-80-26789012",
                "operating_hours": "Daily: 6:30 AM - 10:30 AM",
                "accepted_waste_types": '["wet-waste", "dry-waste", "e-waste"]',
                "latitude": 12.9165,
                "longitude": 77.6101,
                "is_verified": False,
            },
            {
                "name": "Marathahalli Recycling Hub",
                "facility_type": "recycling_center",
                "description": "Integrated recycling center with special e-waste and plastic processing units.",
                "address": "Outer Ring Road, Marathahalli",
                "city": "Bangalore",
                "state": "Karnataka",
                "postal_code": "560037",
                "country": "India",
                "phone": "+91-80-40251234",
                "email": "marathahalli@cleanloop.gov",
                "operating_hours": "Mon-Sat: 8:00 AM - 6:00 PM",
                "accepted_waste_types": '["paper", "plastic", "e-waste", "glass", "metal"]',
                "latitude": 12.9591,
                "longitude": 77.6974,
                "is_verified": True,
            },
        ]

        facilities = []
        for fac_data in facilities_data:
            result = await session.execute(
                select(Facility).where(Facility.name == fac_data["name"])
            )
            existing = result.scalar_one_or_none()

            if not existing:
                facility = Facility(**fac_data)
                session.add(facility)
                await session.flush()
                facilities.append(facility)
                print(f"  ✓ Created facility: {facility.name}")
            else:
                facilities.append(existing)
                print(f"  → Facility exists: {existing.name}")

        await session.commit()

        # ========== SAMPLE COMPLAINTS ==========
        print("\n📝 Creating sample complaints...")

        complaints_data = [
            {
                "reporter_id": users[3].id,  # citizen1
                "title": "Garbage not collected for 3 days",
                "description": "The garbage collection vehicle has not visited our area for the past 3 days. Waste is accumulating and causing bad smell.",
                "address": "15, 3rd Cross, Indiranagar",
                "city": "Bangalore",
                "locality": "Indiranagar",
                "latitude": 12.9784,
                "longitude": 77.6408,
                "priority": ComplaintPriority.HIGH,
                "waste_category_id": categories[0].id,  # Wet waste
                "status": ComplaintStatus.PENDING,
            },
            {
                "reporter_id": users[4].id,  # citizen2
                "title": "Illegal waste dumping near park",
                "description": "People are illegally dumping construction waste near the children's park in our locality. It's dangerous and unsightly.",
                "address": "Near Freedom Park, Jayanagar 4th Block",
                "city": "Bangalore",
                "locality": "Jayanagar",
                "latitude": 12.9250,
                "longitude": 77.5938,
                "priority": ComplaintPriority.URGENT,
                "waste_category_id": categories[5].id,  # Construction waste
                "status": ComplaintStatus.ACKNOWLEDGED,
            },
            {
                "reporter_id": users[3].id,  # citizen1
                "title": "E-waste collection point not functioning",
                "description": "The e-waste collection bin at our society has been full for 2 weeks. No one has come to empty it.",
                "address": "Prestige Lakeside Apartments, Whitefield",
                "city": "Bangalore",
                "locality": "Whitefield",
                "latitude": 12.9698,
                "longitude": 77.7500,
                "priority": ComplaintPriority.MEDIUM,
                "waste_category_id": categories[2].id,  # E-waste
                "status": ComplaintStatus.IN_PROGRESS,
            },
        ]

        for comp_data in complaints_data:
            complaint = Complaint(**comp_data)
            session.add(complaint)
            print(f"  ✓ Created complaint: {complaint.title}")

        await session.commit()

        print("\n✅ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"  • Users: {len(users)} (1 admin, 2 staff, 2 citizens)")
        print(f"  • Categories: {len(categories)}")
        print(f"  • Facilities: {len(facilities)} (8 verified)")
        print(f"  • Sample Complaints: 3")
        print(f"\n🔐 Test Credentials:")
        print(f"  Admin: admin@cleanloop.gov / admin12345")
        print(f"  Staff: staff1@cleanloop.gov / staff12345")
        print(f"  Citizen: citizen1@example.com / citizen12345")


if __name__ == "__main__":
    asyncio.run(seed_database())
