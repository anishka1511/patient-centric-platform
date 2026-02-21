"""
API Routes for symptom assessment agent
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uuid

from config.database import get_db
from routers.schemas import (
    SymptomAssessmentRequest,
    SymptomAssessmentResponse,
    ConversationHistoryResponse
)
from services.agent_orchestrator import agent_orchestrator
from services.conversation_service import conversation_service
from services.geolocation_service import geolocation_service
from services.scraping_adapter import build_scraping_input
from models.message import MessageRole
from config.logging_config import logger

router = APIRouter(prefix="/api", tags=["symptom-assessment"])


def _run_scraping_enrichment(
    scraping_input: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Run scraping recommendation engine with validated input.
    """
    if not scraping_input:
        return None

    try:
        from data_loader import generate_recommendation_response
        return generate_recommendation_response(scraping_input)
    except Exception as exc:
        logger.error(f"Scraping enrichment failed: {exc}", exc_info=True)
        return {
            "error": "Scraping enrichment failed.",
            "details": str(exc),
            "input": scraping_input
        }

def _build_valid_scraping_input(
    assessment_result: Dict[str, Any],
    location_dict: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Build scraping input only when assessment is actionable and required inputs exist.
    """
    category = assessment_result.get("category")
    if category in {"INSUFFICIENT_INFO", "IRRELEVANT"}:
        return None

    payload = build_scraping_input(assessment_result, location_dict)
    coords = payload.get("location", {})
    latitude = coords.get("latitude")
    longitude = coords.get("longitude")
    specialty = payload.get("specialty")

    if latitude is None or longitude is None or not specialty:
        return None

    return payload


@router.post("/assess", response_model=SymptomAssessmentResponse)
async def assess_symptoms(
    http_request: Request,
    request: SymptomAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Assess user's symptoms and provide care navigation guidance
    
    - **message**: User's symptom description
    - **session_id**: Optional session ID for tracking conversations
    - **location**: Optional location (auto-detects from IP if not provided)
    
    Returns assessment with:
    - Extracted symptoms
    - Urgency level  
    - Emergency flag
    - Recommended specialty
    - Care setting
    - Auto-detected or provided location
    - Reasoning and safety advice
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create conversation
        conversation = conversation_service.get_or_create_conversation(db, session_id)
        
        # Get location: Use provided location OR auto-detect from IP
        location_dict = None
        
        if request.location:
            # User provided location manually
            location_dict = request.location.model_dump()
            location_dict["source"] = "user_provided"
            logger.info(f"Using user-provided location: {location_dict.get('city')}")
        else:
            # Auto-detect location from IP
            auto_location = await geolocation_service.get_location_from_request(http_request)
            if auto_location:
                location_dict = auto_location
                logger.info(f"Auto-detected location: {location_dict.get('city')} (source: {location_dict.get('source')})")
        
        # Save user message with location metadata
        message_extra_data = {"location": location_dict} if location_dict else None
        conversation_service.add_message(
            db, 
            conversation.id, 
            MessageRole.USER, 
            request.message,
            extra_data=message_extra_data
        )
        
        # Run assessment with location and db for conversation history
        assessment_result = agent_orchestrator.assess_user_input(
            request.message,
            session_id,
            location=location_dict,
            db=db
        )
        
        # Save assessment to database
        conversation_service.save_assessment(
            db,
            conversation.id,
            assessment_result
        )

        scraping_input = _build_valid_scraping_input(assessment_result, location_dict)
        scraping_recommendations = _run_scraping_enrichment(scraping_input)
        
        # Handle INSUFFICIENT_INFO case - format clarifying questions
        if assessment_result.get("category") == "INSUFFICIENT_INFO":
            clarifying_questions = assessment_result.get("clarifying_questions", [])
            questions_text = "\n\n🤔 Please provide more details:\n\n" + "\n".join(f"• {q}" for q in clarifying_questions)
            reasoning = assessment_result.get("message", "I need more details.") + questions_text if clarifying_questions else assessment_result.get("reason", "")
            
            response = SymptomAssessmentResponse(
                symptoms_identified=[],
                urgency_level="low",
                emergency_flag=False,
                recommended_specialty="Awaiting clarification",
                care_setting="clinic",
                reasoning=reasoning,
                safety_advice=None,
                session_id=session_id,
                user_location=location_dict,
                scraping_input=scraping_input,
                scraping_recommendations=scraping_recommendations,
                disclaimer=agent_orchestrator.get_health_disclaimer()
            )
        # Handle IRRELEVANT case - non-medical input
        elif assessment_result.get("category") == "IRRELEVANT":
            suggestions = assessment_result.get("suggestions", [])
            suggestions_text = "\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions) if suggestions else ""
            
            response = SymptomAssessmentResponse(
                symptoms_identified=[],
                urgency_level="low",
                emergency_flag=False,
                recommended_specialty="N/A",
                care_setting="N/A",
                reasoning=assessment_result.get("message", "Please describe your symptoms.") + suggestions_text,
                safety_advice=None,
                session_id=session_id,
                user_location=location_dict,
                scraping_input=scraping_input,
                scraping_recommendations=scraping_recommendations,
                disclaimer=agent_orchestrator.get_health_disclaimer()
            )
        # Normal medical assessment
        else:
            response = SymptomAssessmentResponse(
                symptoms_identified=assessment_result.get("symptoms_identified", []),
                urgency_level=assessment_result.get("urgency_level", "medium"),
                emergency_flag=assessment_result.get("emergency_flag", False),
                recommended_specialty=assessment_result.get("recommended_specialty", "General Physician"),
                care_setting=assessment_result.get("care_setting", "clinic"),
                reasoning=assessment_result.get("reasoning", ""),
                safety_advice=assessment_result.get("safety_advice"),
                session_id=session_id,
                user_location=location_dict,
                scraping_input=scraping_input,
                scraping_recommendations=scraping_recommendations,
                disclaimer=agent_orchestrator.get_health_disclaimer()
            )
        
        # Save assistant response
        response_text = (
            f"Symptoms identified: {', '.join(response.symptoms_identified)}\n"
            f"Urgency: {response.urgency_level}\n"
            f"Recommended: {response.recommended_specialty} at {response.care_setting}\n"
            f"Reasoning: {response.reasoning}"
        )
        conversation_service.add_message(
            db,
            conversation.id,
            MessageRole.ASSISTANT,
            response_text
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in /assess endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/conversation/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a session
    
    - **session_id**: Session identifier
    
    Returns full conversation history with messages and assessments
    """
    try:
        history = conversation_service.get_conversation_history(db, session_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/disclaimer")
async def get_disclaimer():
    """
    Get medical disclaimer text
    
    Returns the medical disclaimer that should be shown to users
    """
    return {
        "disclaimer": agent_orchestrator.get_health_disclaimer()
    }
