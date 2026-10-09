"""Pydantic schemas package."""

from app.schemas.analytics import (
    AnalyticsOverview,
    CategoryStatsResponse,
    ComplaintTrendResponse,
    HotspotResponse,
    HotspotsListResponse,
    TimeSeriesDataPoint,
)
from app.schemas.complaint import (
    ComplaintBase,
    ComplaintCreate,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintResponse,
    ComplaintStatusHistoryDetail,
    ComplaintStatusHistoryResponse,
    ComplaintStatusUpdate,
    ComplaintSyncResponse,
    ComplaintUpdate,
    FeedbackCreate,
    FeedbackResponse,
)
from app.schemas.facility import (
    FacilityBase,
    FacilityCreate,
    FacilityNearbyRequest,
    FacilityResponse,
    FacilityUpdate,
    FacilityVerificationRequest,
    FacilityWithDistance,
)
from app.schemas.user import (
    Token,
    TokenPayload,
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.schemas.waste import (
    DisposalRuleCreate,
    DisposalRuleDetailResponse,
    DisposalRuleResponse,
    WasteCategoryCreate,
    WasteCategoryResponse,
    WasteClassificationRequest,
    WasteClassificationResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Waste schemas
    "WasteCategoryCreate",
    "WasteCategoryResponse",
    "WasteClassificationRequest",
    "WasteClassificationResponse",
    "DisposalRuleCreate",
    "DisposalRuleResponse",
    "DisposalRuleDetailResponse",
    # Facility schemas
    "FacilityBase",
    "FacilityCreate",
    "FacilityUpdate",
    "FacilityResponse",
    "FacilityNearbyRequest",
    "FacilityWithDistance",
    "FacilityVerificationRequest",
    # Complaint schemas
    "ComplaintBase",
    "ComplaintCreate",
    "ComplaintUpdate",
    "ComplaintResponse",
    "ComplaintDetailResponse",
    "ComplaintListResponse",
    "ComplaintStatusUpdate",
    "ComplaintStatusHistoryResponse",
    "ComplaintStatusHistoryDetail",
    "ComplaintSyncResponse",
    "FeedbackCreate",
    "FeedbackResponse",
    # Analytics schemas
    "AnalyticsOverview",
    "HotspotResponse",
    "HotspotsListResponse",
    "CategoryStatsResponse",
    "ComplaintTrendResponse",
    "TimeSeriesDataPoint",
]
