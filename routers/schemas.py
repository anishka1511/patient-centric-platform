"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SymptomAssessmentRequest(BaseModel):
    """Request to assess symptoms"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's symptom description")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")
    
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
