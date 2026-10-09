"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, complaints, facilities, waste

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(waste.router)
api_router.include_router(facilities.router)
api_router.include_router(complaints.router)
api_router.include_router(analytics.router)
