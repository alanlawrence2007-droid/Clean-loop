"""Pydantic schemas package."""

from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenData
from app.schemas.waste import (
    WasteCategoryCreate,
    WasteCategoryResponse,
    WasteCategoryUpdate,
    DisposalRuleCreate,
    DisposalRuleResponse,
    DisposalRuleUpdate,
    WasteClassificationRequest,
    WasteClassificationResponse,
)
from app.schemas.facility import (
    FacilityCreate,
    FacilityResponse,
    FacilityUpdate,
    FacilityNearbyRequest,
    FacilityListResponse,
)
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintUpdate,
    ComplaintStatusUpdate,
    ComplaintStatusHistoryResponse,
    ComplaintListResponse,
    ComplaintSyncRequest,
    ComplaintSyncResponse,
    FeedbackCreate,
    FeedbackResponse,
)
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    HotspotResponse,
    HotspotListResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    # Waste
    "WasteCategoryCreate",
    "WasteCategoryResponse",
    "WasteCategoryUpdate",
    "DisposalRuleCreate",
    "DisposalRuleResponse",
    "DisposalRuleUpdate",
    "WasteClassificationRequest",
    "WasteClassificationResponse",
    # Facility
    "FacilityCreate",
    "FacilityResponse",
    "FacilityUpdate",
    "FacilityNearbyRequest",
    "FacilityListResponse",
    # Complaint
    "ComplaintCreate",
    "ComplaintResponse",
    "ComplaintUpdate",
    "ComplaintStatusUpdate",
    "ComplaintStatusHistoryResponse",
    "ComplaintListResponse",
    "ComplaintSyncRequest",
    "ComplaintSyncResponse",
    "FeedbackCreate",
    "FeedbackResponse",
    # Analytics
    "AnalyticsOverviewResponse",
    "HotspotResponse",
    "HotspotListResponse",
]