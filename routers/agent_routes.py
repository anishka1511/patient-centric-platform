"""
API Routes for symptom assessment agent
"""
from fastapi import APIRouter, Depends, HTTPException
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
from models.message import MessageRole
from config.logging_config import logger

router = APIRouter(prefix="/api", tags=["symptom-assessment"])


@router.post("/assess", response_model=SymptomAssessmentResponse)
async def assess_symptoms(
    request: SymptomAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Assess user's symptoms and provide care navigation guidance
    
    - **message**: User's symptom description
    - **session_id**: Optional session ID for tracking conversations
    
    Returns assessment with:
    - Extracted symptoms
    - Urgency level  
    - Emergency flag
    - Recommended specialty
    - Care setting
    - Reasoning and safety advice
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create conversation
        conversation = conversation_service.get_or_create_conversation(db, session_id)
        
        # Save user message
        conversation_service.add_message(
            db, 
            conversation.id, 
            MessageRole.USER, 
            request.message
        )
        
        # Run assessment
        assessment_result = agent_orchestrator.assess_user_input(
            request.message,
            session_id
        )
        
        # Save assessment to database
        conversation_service.save_assessment(
            db,
            conversation.id,
            assessment_result
        )
        
        # Prepare response
        response = SymptomAssessmentResponse(
            symptoms_identified=assessment_result.get("symptoms_identified", []),
            urgency_level=assessment_result.get("urgency_level", "medium"),
            emergency_flag=assessment_result.get("emergency_flag", False),
            recommended_specialty=assessment_result.get("recommended_specialty", "General Physician"),
            care_setting=assessment_result.get("care_setting", "clinic"),
            reasoning=assessment_result.get("reasoning", ""),
            safety_advice=assessment_result.get("safety_advice"),
            session_id=session_id,
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
