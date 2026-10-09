"""API router configuration."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, waste, facilities, complaints, sync, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(waste.router, prefix="/waste", tags=["Waste Management"])
api_router.include_router(facilities.router, prefix="/facilities", tags=["Facilities"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(sync.router, prefix="/sync", tags=["Offline Sync"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])