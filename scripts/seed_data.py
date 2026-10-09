"""Seed data script for Clean Loop backend."""

import asyncio
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.models.waste import WasteCategory, DisposalRule
from app.models.facility import Facility
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


async def create_test_users(db: AsyncSession):
    """Create test users for each role."""
    test_users = [
        {
            "email": "admin@cleanloop.gov",
            "hashed_password": hash_password("admin12345"),
            "full_name": "System Administrator",
            "role": UserRole.ADMIN,
            "is_active": True,
        },
        {
            "email": "staff1@cleanloop.gov",
            "hashed_password": hash_password("staff12345"),
            "full_name": "Municipal Staff Member",
            "role": UserRole.MUNICIPAL_STAFF,
            "is_active": True,
        },
        {
            "email": "citizen1@example.com",
            "hashed_password": hash_password("citizen12345"),
            "full_name": "Concerned Citizen",
            "role": UserRole.CITIZEN,
            "is_active": True,
        },
        {
            "email": "citizen2@example.com",
            "hashed_password": hash_password("citizen12345"),
            "full_name": "Eco-conscious Resident",
            "role": UserRole.CITIZEN,
            "is_active": True,
        },
    ]

    users = []
    for user_data in test_users:
        # Check if user already exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        existing = result.scalar_one_or_none()
        if not existing:
            user = User(**user_data)
            db.add(user)
            users.append(user)
        else:
            users.append(existing)

    await db.commit()
    for user in users:
        await db.refresh(user)

    print(f"Created/verified {len(users)} test users")
    return users


async def create_waste_categories(db: AsyncSession):
    """Create waste categories."""
    categories_data = [
        {
            "name": "Wet Waste",
            "slug": "wet-waste",
            "description": "Organic waste from kitchen and food preparation",
            "color_code": "#008000",
            "icon": "leaf",
        },
        {
            "name": "Dry Waste",
            "slug": "dry-waste",
            "description": "Recyclable materials like paper, plastic, metal, glass",
            "color_code": "#FFA500",
            "icon": "recycle",
        },
        {
            "name": "E-Waste",
            "slug": "e-waste",
            "description": "Electronic and electrical equipment waste",
            "color_code": "#800080",
            "icon": "laptop",
        },
        {
            "name": "Sanitary Waste",
            "slug": "sanitary-waste",
            "description": "Hygiene and medical waste like diapers, sanitary pads",
            "color_code": "#FF0000",
            "icon": "hospital",
        },
        {
            "name": "Hazardous Waste",
            "slug": "hazardous-waste",
            "description": "Chemicals, paints, oils, pesticides and other toxic materials",
            "color_code": "#FF00FF",
            "icon": "biohazard",
        },
        {
            "name": "Construction Waste",
            "slug": "construction-waste",
            "description": "Debris from construction, renovation, and demolition",
            "color_code": "#8B4513",
            "icon": "hard-hat",
        },
        {
            "name": "Garden Waste",
            "slug": "garden-waste",
            "description": "Organic waste from gardens and yards",
            "color_code": "#006400",
            "icon": "tree",
        },
    ]

    categories = []
    for cat_data in categories_data:
        # Check if category already exists
        from sqlalchemy import select
        result = await db.execute(
            select(WasteCategory).where(WasteCategory.slug == cat_data["slug"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            category = WasteCategory(**cat_data)
            db.add(category)
            categories.append(category)
        else:
            categories.append(existing)

    await db.commit()
    for category in categories:
        await db.refresh(category)

    print(f"Created/verified {len(categories)} waste categories")
    return categories


async def create_disposal_rules(db: AsyncSession, categories: list):
    """Create disposal rules for waste categories."""
    # Map category names to objects
    category_map = {cat.name: cat for cat in categories}

    rules_data = [
        # Wet Waste Rules
        {
            "category_id": category_map["Wet Waste"].id,
            "title": "Kitchen Food Waste Composting",
            "description": "Compost food scraps and organic kitchen waste",
            "instructions": "Separate food waste from packaging. Use a compost bin or municipal organic waste collection.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Daily",
            "pickup_time": "6:00 AM - 8:00 AM",
            "tips": "Line your bin with newspaper to reduce moisture and odor.",
            "warnings": "Do not mix with plastic or non-biodegradable materials.",
            "priority": 10,
        },
        {
            "category_id": category_map["Wet Waste"].id,
            "title": "General Wet Waste Disposal",
            "description": "Standard disposal for organic kitchen waste",
            "instructions": "Wrap wet waste in newspaper before disposing in green bin.",
            "priority": 5,
        },

        # Dry Waste Rules
        {
            "category_id": category_map["Dry Waste"].id,
            "title": "Paper and Cardboard Recycling",
            "description": "Recycle clean paper, cardboard, and packaging materials",
            "instructions": "Flatten cardboard boxes. Keep paper dry and free from food contamination.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Twice weekly",
            "pickup_time": "8:00 AM - 10:00 AM",
            "tips": "Remove plastic coating from paper cups before recycling.",
            "priority": 10,
        },
        {
            "category_id": category_map["Dry Waste"].id,
            "title": "Plastic and Metal Recycling",
            "description": "Recycle plastic bottles, containers, and metal cans",
            "instructions": "Rinse containers before recycling. Remove lids and labels when possible.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Twice weekly",
            "pickup_time": "8:00 AM - 10:00 AM",
            "tips": "Check plastic recycling codes - #1 and #2 are most commonly accepted.",
            "priority": 10,
        },
        {
            "category_id": category_map["Dry Waste"].id,
            "title": "General Dry Waste Disposal",
            "description": "Standard disposal for recyclable dry waste",
            "instructions": "Keep dry waste clean and dry. Place in blue recycling bin.",
            "priority": 5,
        },

        # E-Waste Rules
        {
            "category_id": category_map["E-Waste"].id,
            "title": "Electronic Waste Collection",
            "description": "Proper disposal of electronic and electrical equipment",
            "instructions": "Take e-waste to authorized collection centers. Do not dispose in regular trash.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Monthly collection drives",
            "pickup_time": "10:00 AM - 4:00 PM",
            "tips": "Remove batteries before disposing of electronic devices.",
            "warnings": "E-waste contains hazardous materials like lead, mercury, and cadmium.",
            "priority": 15,
        },
        {
            "category_id": category_map["E-Waste"].id,
            "title": "General E-Waste Disposal",
            "description": "Standard disposal for electronic waste",
            "instructions": "Store e-waste in a dry place until collection day.",
            "priority": 5,
        },

        # Sanitary Waste Rules
        {
            "category_id": category_map["Sanitary Waste"].id,
            "title": "Sanitary Waste Disposal",
            "description": "Proper disposal of hygiene and medical waste",
            "instructions": "Wrap sanitary waste in newspaper or biodegradable bag before disposal.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Daily",
            "pickup_time": "6:00 AM - 8:00 AM",
            "tips": "Use a separate bin with lid for sanitary waste.",
            "warnings": "Do not flush sanitary products down the toilet.",
            "priority": 10,
        },

        # Hazardous Waste Rules
        {
            "category_id": category_map["Hazardous Waste"].id,
            "title": "Hazardous Waste Collection",
            "description": "Safe disposal of chemicals, paints, oils, and toxic materials",
            "instructions": "Store hazardous materials in original containers with labels intact.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Quarterly collection events",
            "pickup_time": "9:00 AM - 1:00 PM",
            "tips": "Never mix different hazardous chemicals together.",
            "warnings": "Hazardous waste requires special handling to prevent environmental contamination.",
            "priority": 20,
        },
        {
            "category_id": category_map["Hazardous Waste"].id,
            "title": "General Hazardous Waste Disposal",
            "description": "Standard disposal for hazardous materials",
            "instructions": "Keep hazardous waste in sealed, labeled containers away from children and pets.",
            "priority": 5,
        },

        # Construction Waste Rules
        {
            "category_id": category_map["Construction Waste"].id,
            "title": "Construction Debris Disposal",
            "description": "Proper disposal of construction and demolition waste",
            "instructions": "Separate materials for recycling when possible. Use authorized disposal sites.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "On-demand for large quantities",
            "tips": "Consider donating usable materials to reconstruction projects.",
            "warnings": "Construction waste may contain hazardous materials like asbestos in older buildings.",
            "priority": 10,
        },

        # Garden Waste Rules
        {
            "category_id": category_map["Garden Waste"].id,
            "title": "Garden Waste Composting",
            "description": "Compost leaves, branches, and organic garden waste",
            "instructions": "Chop large branches into smaller pieces for faster composting.",
            "locality": "Bangalore Urban",
            "pickup_schedule": "Weekly",
            "pickup_time": "7:00 AM - 9:00 AM",
            "tips": "Mix green and brown materials for optimal composting.",
            "priority": 10,
        },
        {
            "category_id": category_map["Garden Waste"].id,
            "title": "General Garden Waste Disposal",
            "description": "Standard disposal for garden organic waste",
            "instructions": "Place garden waste in green bin for organic waste collection.",
            "priority": 5,
        },
    ]

    rules = []
    for rule_data in rules_data:
        # Check if rule already exists (by title and category)
        from sqlalchemy import select
        result = await db.execute(
            select(DisposalRule).where(
                and_(
                    DisposalRule.title == rule_data["title"],
                    DisposalRule.category_id == rule_data["category_id"],
                )
            )
        )
        existing = result.scalar_one_or_none()
        if not existing:
            rule = DisposalRule(**rule_data)
            db.add(rule)
            rules.append(rule)
        else:
            rules.append(existing)

    await db.commit()
    for rule in rules:
        await db.refresh(rule)

    print(f"Created/verified {len(rules)} disposal rules")
    return rules


async def create_facilities(db: AsyncSession):
    """Create sample waste management facilities."""
    facilities_data = [
        {
            "name": "Electronic City Recycling Center",
            "facility_type": "recycling_center",
            "description": "Modern recycling facility serving Electronic City and surrounding areas",
            "address": "Plot No. 74, Electronics City Phase 1",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560100",
            "phone": "080-41234567",
            "email": "info@ecityrecycling.gov.in",
            "website": "https://ecityrecycling.gov.in",
            "operating_hours": "Monday-Saturday: 8:00 AM - 6:00 PM",
            "accepted_waste_types": '["paper", "plastic", "metal", "glass", "e-waste"]',
            "latitude": 12.8456,
            "longitude": 77.6603,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
        {
            "name": "Whitefield Composting Facility",
            "facility_type": "composting_facility",
            "description": "Organic waste composting facility for wet and garden waste",
            "address": "ITPL Main Road, Whitefield",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560066",
            "phone": "080-28456789",
            "email": "compost@whitefield.gov.in",
            "website": "https://whitefieldcompost.gov.in",
            "operating_hours": "Monday-Sunday: 6:00 AM - 8:00 PM",
            "accepted_waste_types": '["wet waste", "garden waste"]',
            "latitude": 12.9698,
            "longitude": 77.7500,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
        {
            "name": "Jayanagar Hazardous Waste Depot",
            "facility_type": "hazardous_waste_depot",
            "description": "Specialized facility for hazardous chemical and toxic waste disposal",
            "address": "11th Block, Jayanagar",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560011",
            "phone": "080-22445566",
            "email": "hazmat@jayanagar.gov.in",
            "website": "https://jayanagarhazmat.gov.in",
            "operating_hours": "Monday-Friday: 9:00 AM - 5:00 PM",
            "accepted_waste_types": '["chemicals", "paints", "oils", "pesticides", "batteries"]',
            "latitude": 12.9279,
            "longitude": 77.5937,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
        {
            "name": "Koramangala E-Waste Center",
            "facility_type": "e_waste_center",
            "description": "Dedicated center for electronic waste collection and recycling",
            "address": "80 Feet Road, Koramangala 5th Block",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560095",
            "phone": "080-41556677",
            "email": "ewaste@koramangala.gov.in",
            "website": "https://koramangalaewaste.gov.in",
            "operating_hours": "Monday-Saturday: 10:00 AM - 7:00 PM",
            "accepted_waste_types": '["computers", "phones", "tv", "appliances", "batteries"]',
            "latitude": 12.9352,
            "longitude": 77.6245,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
        {
            "name": "Banashankari Waste Collection Point",
            "facility_type": "waste_collection_point",
            "description": "Neighborhood waste collection point for segregated waste",
            "address": "Banashankari 2nd Stage, Near BBMP Office",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560070",
            "phone": "080-26789012",
            "email": "collection@banashankari.gov.in",
            "website": "https://banashankaricollection.gov.in",
            "operating_hours": "Daily: 6:00 AM - 8:00 PM",
            "accepted_waste_types": '["wet waste", "dry waste", "sanitary waste"]',
            "latitude": 12.9017,
            "longitude": 77.5601,
            "is_verified": False,
        },
        {
            "name": "Indiranagar Transfer Station",
            "facility_type": "transfer_station",
            "description": "Intermediate station for waste transfer to processing facilities",
            "address": "100 Feet Road, Indiranagar",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560038",
            "phone": "080-25551234",
            "email": "transfer@indiranagar.gov.in",
            "website": "https://indiranagartransfer.gov.in",
            "operating_hours": "Monday-Saturday: 5:00 AM - 9:00 PM",
            "accepted_waste_types": '["mixed waste", "construction debris"]',
            "latitude": 12.9784,
            "longitude": 77.6408,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
        {
            "name": "Malleswaram Landfill Site",
            "facility_type": "landfill",
            "description": "Engineered landfill for non-recyclable and inert waste",
            "address": "Malleswaram West, Near Sankey Tank",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560003",
            "phone": "080-23344556",
            "email": "landfill@malleswaram.gov.in",
            "website": "https://malleswaramlandfill.gov.in",
            "operating_hours": "Monday-Sunday: 6:00 AM - 6:00 PM",
            "accepted_waste_types": '["inert waste", "construction debris", "non-recyclable"]',
            "latitude": 13.0176,
            "longitude": 77.5728,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc),
        },
    ]

    facilities = []
    for fac_data in facilities_data:
        # Check if facility already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Facility).where(Facility.name == fac_data["name"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            facility = Facility(**fac_data)
            db.add(facility)
            facilities.append(facility)
        else:
            facilities.append(existing)

    await db.commit()
    for facility in facilities:
        await db.refresh(facility)

    print(f"Created/verified {len(facilities)} facilities")
    return facilities


async def create_sample_complaints(db: AsyncSession, users: list, categories: list, facilities: list):
    """Create sample complaints for demonstration."""
    # Get test users
    admin_user = next((u for u in users if u.email == "admin@cleanloop.gov"), None)
    staff_user = next((u for u in users if u.email == "staff1@cleanloop.gov"), None)
    citizen1 = next((u for u in users if u.email == "citizen1@example.com"), None)
    citizen2 = next((u for u in users if u.email == "citizen2@example.com"), None)

    # Get categories
    wet_waste = next((c for c in categories if c.name == "Wet Waste"), None)
    dry_waste = next((c for c in categories if c.name == "Dry Waste"), None)
    e_waste = next((c for c in categories if c.name == "E-Waste"), None)

    # Get facilities
    recycling_center = next((f for f in facilities if f.name == "Electronic City Recycling Center"), None)
    composting_facility = next((f for f in facilities if f.name == "Whitefield Composting Facility"), None)
    e_waste_center = next((f for f in facilities if f.name == "Koramangala E-Waste Center"), None)

    complaints_data = [
        {
            "title": "Illegal dumping of construction debris in Koramangala",
            "description": "Large amounts of construction debris and rubble dumped illegally on 1st Main Road, Koramangala. Creating safety hazard and environmental concern.",
            "waste_category_id": dry_waste.id if dry_waste else None,
            "address": "1st Main Road, Koramangala 5th Block",
            "city": "Bangalore",
            "locality": "Koramangala",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "priority": ComplaintPriority.HIGH,
            "photo_url": "https://example.com/complaint1.jpg",
            "reporter_id": citizen1.id if citizen1 else None,
            "facility_id": recycling_center.id if recycling_center else None,
            "status": ComplaintStatus.IN_PROGRESS,
            "client_generated_id": uuid.uuid4(),
        },
        {
            "title": "Wet waste not being collected from Whitefield apartments",
            "description": "Wet waste (food scraps, vegetable peels) not collected for past 3 days from Whitefield apartment complexes. Causing odor and hygiene issues.",
            "waste_category_id": wet_waste.id if wet_waste else None,
            "address": "ITPL Main Road, Whitefield",
            "city": "Bangalore",
            "locality": "Whitefield",
            "latitude": 12.9698,
            "longitude": 77.7500,
            "priority": ComplaintPriority.MEDIUM,
            "photo_url": "https://example.com/complaint2.jpg",
            "reporter_id": citizen2.id if citizen2 else None,
            "facility_id": composting_facility.id if composting_facility else None,
            "status": ComplaintStatus.ACKNOWLEDGED,
            "client_generated_id": uuid.uuid4(),
        },
        {
            "title": "E-waste accumulated in Electronic City apartments",
            "description": "Residents have accumulated electronic waste (old phones, chargers, batteries) with no proper disposal facility nearby.",
            "waste_category_id": e_waste.id if e_waste else None,
            "address": "Electronic City Phase 1",
            "city": "Bangalore",
            "locality": "Electronic City",
            "latitude": 12.8456,
            "longitude": 77.6603,
            "priority": ComplaintPriority.MEDIUM,
            "reporter_id": citizen1.id if citizen1 else None,
            "facility_id": e_waste_center.id if e_waste_center else None,
            "status": ComplaintStatus.PENDING,
            "client_generated_id": uuid.uuid4(),
        },
        {
            "title": "Sanitary waste disposal issue in Indiranagar",
            "description": "Improper disposal of sanitary waste in public bins causing health hazards and unpleasant smell.",
            "waste_category_id": wet_waste.id if wet_waste else None,  # Using wet waste as placeholder
            "address": "100 Feet Road, Indiranagar",
            "city": "Bangalore",
            "locality": "Indiranagar",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "priority": ComplaintPriority.LOW,
            "reporter_id": citizen2.id if citizen2 else None,
            "status": ComplaintStatus.RESOLVED,
            "resolution_notes": "Issue addressed through awareness campaign and installation of dedicated sanitary waste bins.",
            "resolved_at": datetime.now(timezone.utc),
            "resolved_by": staff_user.id if staff_user else None,
            "client_generated_id": uuid.uuid4(),
        },
        {
            "title": "Hazardous chemical spill near Bannerghatta Road",
            "description": "Small spill of hazardous chemicals (appears to be paint thinner) near storm drain on Bannerghatta Road. Requires immediate attention.",
            "waste_category_id": None,  # Hazardous waste category
            "address": "Bannerghatta Road, IIMB",
            "city": "Bangalore",
            "locality": "Bannerghatta",
            "latitude": 12.9076,
            "longitude": 77.5971,
            "priority": ComplaintPriority.URGENT,
            "reporter_id": citizen1.id if citizen1 else None,
            "status": ComplaintStatus.PENDING,
            "client_generated_id": uuid.uuid4(),
        },
    ]

    from sqlalchemy import and_

    complaints = []
    for comp_data in complaints_data:
        # Check if complaint already exists by client_generated_id
        if comp_data.get("client_generated_id"):
            result = await db.execute(
                select(Complaint).where(Complaint.client_generated_id == comp_data["client_generated_id"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                complaint = Complaint(**comp_data)
                db.add(complaint)
                complaints.append(complaint)
            else:
                complaints.append(existing)
        else:
            complaint = Complaint(**comp_data)
            db.add(complaint)
            complaints.append(complaint)

    await db.commit()
    for complaint in complaints:
        await db.refresh(complaint)

    print(f"Created/verified {len(complaints)} sample complaints")
    return complaints


async def main():
    """Main seeding function."""
    print("Starting database initialization...")
    await init_db()

    print("Creating database session...")
    async with AsyncSessionLocal() as db:
        try:
            # Create test users
            users = await create_test_users(db)

            # Create waste categories
            categories = await create_waste_categories(db)

            # Create disposal rules
            await create_disposal_rules(db, categories)

            # Create facilities
            facilities = await create_facilities(db)

            # Create sample complaints
            await create_sample_complaints(db, users, categories, facilities)

            print("✅ Seed data creation completed successfully!")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())