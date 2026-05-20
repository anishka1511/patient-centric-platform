"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserLocation(BaseModel):
    """User's geographical location"""
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")
    postal_code: Optional[str] = Field(None, description="ZIP/Postal code")
    source: Optional[str] = Field(None, description="Location source: user_provided, ipapi.co, ipinfo.io, ip-api.com, default")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 19.0760,
                "longitude": 72.8777,
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400001",
                "source": "auto_detected"
            }
        }


class SymptomAssessmentRequest(BaseModel):
    """Request to assess symptoms"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's symptom description")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")
    location: Optional[UserLocation] = Field(None, description="User's location (optional - will auto-detect from IP if not provided)")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I have severe chest pain and shortness of breath",
                "session_id": "user123-session456"
            }
        }


class SymptomAssessmentResponse(BaseModel):
    """Response with symptom assessment"""
    symptoms_identified: List[str]
    urgency_level: str
    emergency_flag: bool
    recommended_specialty: str
    care_setting: str
    reasoning: str
    safety_advice: Optional[str] = None
    session_id: Optional[str] = None
    user_location: Optional[UserLocation] = Field(None, description="User's location if provided")
    scraping_input: Optional[Dict[str, Any]] = Field(
        None,
        description="Validated payload that was sent to the scraping/recommendation engine"
    )
    scraping_recommendations: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional downstream recommendations from scraping/recommendation engine"
    )
    disclaimer: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms_identified": ["chest pain", "shortness of breath"],
                "urgency_level": "high",
                "emergency_flag": True,
                "recommended_specialty": "Cardiology",
                "care_setting": "emergency_department",
                "reasoning": "Chest pain with breathing difficulty requires urgent evaluation.",
                "safety_advice": "Seek immediate medical attention or go to the nearest emergency department.",
                "session_id": "user123-session456",
                "disclaimer": "⚠️ This is not a medical diagnosis..."
            }
        }


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history"""
    session_id: str
    messages: List[Dict]
    assessments: List[Dict]
    created_at: datetime
    updated_at: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    llm_service: str


class ReviewCreateRequest(BaseModel):
    """Create a new doctor/facility review"""
    doctor_name: str = Field(..., min_length=1, max_length=200)
    doctor_specialty: Optional[str] = Field(None, max_length=200)
    facility_name: Optional[str] = Field(None, max_length=200)
    facility_type: Optional[str] = Field(None, max_length=100)
    facility_location: Optional[str] = Field(None, max_length=200)
    reviewer_name: Optional[str] = Field(None, max_length=120)
    comment: str = Field(..., min_length=1, max_length=5000)
    overall_rating: float = Field(..., ge=0, le=5)
    factor_ratings: Dict[str, float] = Field(default_factory=dict)
    additional_charges_paid: Optional[bool] = None
    additional_charges_amount: Optional[str] = Field(None, max_length=120)
    additional_charges_explained: Optional[str] = Field(None, max_length=200)


class ReviewResponse(BaseModel):
    """Persisted review response payload"""
    id: str
    doctor_name: str
    doctor_specialty: Optional[str] = None
    facility_name: Optional[str] = None
    facility_type: Optional[str] = None
    facility_location: Optional[str] = None
    reviewer_name: Optional[str] = None
    comment: str
    overall_rating: float
    factor_ratings: Dict[str, float]
    additional_charges_paid: Optional[bool] = None
    additional_charges_amount: Optional[str] = None
    additional_charges_explained: Optional[str] = None
    created_at: datetime


class ReviewListResponse(BaseModel):
    """Filtered review list"""
    reviews: List[ReviewResponse]
