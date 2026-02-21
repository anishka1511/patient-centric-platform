"""
Agent Orchestration Service
Coordinates the full symptom assessment pipeline using LLM for classification
"""
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from services.llm_service import llm_service
from services.conversation_service import conversation_service
from utils.emergency_rules import emergency_detector
from utils.specialty_mapper import specialty_mapper
from config.logging_config import logger


class AgentOrchestrator:
    """
    Orchestrates the full symptom assessment workflow using LLM:
    1. LLM classifies input and extracts symptoms (single call)
    2. Detect emergency (LLM + rules backup)
    3. Assess symptoms with LLM
    4. Map to specialty
    5. Return structured response
    """
    
    def __init__(self):
        self.llm_service = llm_service
        self.conversation_service = conversation_service
        self.emergency_detector = emergency_detector
        self.specialty_mapper = specialty_mapper
    
    def assess_user_input(
        self, 
        user_message: str, 
        session_id: Optional[str] = None, 
        location: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Full assessment pipeline for user input
        
        Args:
            user_message: User's symptom description
            session_id: Optional session ID for conversation tracking
            location: Optional user location (lat/long, city, etc.)
            db: Optional database session for fetching conversation history
            
        Returns:
            Complete assessment result as dict
        """
        logger.info(f"Starting assessment for message: '{user_message[:50]}...'")
        if location:
            logger.info(f"User location: {location.get('city', 'Unknown')}, {location.get('state', '')}")
        
        # Fetch conversation history if db session provided
        conversation_history = []
        if db and session_id:
            conversation_history = self.conversation_service.get_recent_messages(db, session_id, limit=5)
            if conversation_history:
                logger.info(f"Retrieved {len(conversation_history)} recent messages for context")
        
        try:
            # Step 1: LLM-based Input Classification + Symptom Extraction (combined)
            classification = self.llm_service.classify_input(user_message, history=conversation_history)
            
            category = classification.get("category")
            symptoms = classification.get("symptoms", [])
            llm_emergency = classification.get("emergency", False)
            
            logger.info(f"LLM classified as: {category} with {len(symptoms)} symptoms")
            
            # Handle IRRELEVANT inputs (greetings, small talk)
            if category == "IRRELEVANT":
                return {
                    "category": "IRRELEVANT",
                    "message": classification.get("message", "I'm here to help with medical symptom assessment."),
                    "suggestions": [
                        "Please describe any symptoms or health concerns you're experiencing.",
                        "Example: 'headache for 2 days', 'fever and cough', 'cherry angioma'"
                    ],
                    "session_id": session_id,
                    "user_input": user_message,
                    "user_location": location
                }
            
            # Handle INSUFFICIENT_INFO (vague symptoms, needs clarification)
            if category == "INSUFFICIENT_INFO":
                return {
                    "category": "INSUFFICIENT_INFO",
                    "message": "I need more details to provide an accurate assessment.",
                    "reason": classification.get("reason"),
                    "clarifying_questions": classification.get("clarifying_questions", [
                        "Where is the symptom located?",
                        "How long have you had this symptom?",
                        "How severe is it? (mild/moderate/severe)"
                    ]),
                    "session_id": session_id,
                    "user_input": user_message,
                    "user_location": location
                }
            
            # EMERGENCY and VALID_MEDICAL continue to full assessment
            
            # Step 2: Rule-based emergency detection (safety backup)
            rule_emergency, pattern, reason = self.emergency_detector.detect_emergency(
                user_message, symptoms
            )
            rule_urgency = self.emergency_detector.assess_urgency(user_message, symptoms)
            
            if rule_emergency:
                logger.warning(f"Emergency detected by rules: {reason}")
            if llm_emergency:
                logger.warning("Emergency detected by LLM classification")
            
            # Step 3: LLM assessment (detailed analysis of symptoms)
            llm_assessment = self.llm_service.assess_symptoms(symptoms, history=conversation_history)
            
            # Step 4: Override with emergency detection (LLM classification or rules)
            if (llm_emergency or rule_emergency) and not llm_assessment.get("emergency_flag"):
                logger.warning("Overriding LLM assessment - emergency detected")
                llm_assessment["emergency_flag"] = True
                llm_assessment["urgency_level"] = "high"
                emergency_reason = reason if rule_emergency else "Emergency symptoms identified"
                llm_assessment["safety_advice"] = (
                    "URGENT: Seek immediate medical attention or go to the nearest emergency department. "
                    f"Detected: {emergency_reason}"
                )
            
            # Ensure urgency is at least as high as rules suggest
            urgency_order = {"low": 0, "medium": 1, "high": 2}
            llm_urgency = llm_assessment.get("urgency_level", "low")
            if urgency_order.get(rule_urgency, 0) > urgency_order.get(llm_urgency, 0):
                llm_assessment["urgency_level"] = rule_urgency
            
            # Step 5: Augment specialty recommendation
            mapped_specialty, confidence = self.specialty_mapper.map_specialty(
                symptoms, 
                llm_assessment.get("recommended_specialty")
            )
            
            # Use mapped specialty if confidence is high
            if confidence > 0.7:
                llm_assessment["recommended_specialty"] = mapped_specialty
            
            # Step 6: Determine care setting
            care_setting = self.specialty_mapper.get_care_setting(
                llm_assessment.get("urgency_level", "low"),
                llm_assessment.get("emergency_flag", False)
            )
            llm_assessment["care_setting"] = care_setting
            
            # Step 7: Add metadata
            result = {
                **llm_assessment,
                "session_id": session_id,
                "user_input": user_message,
                "user_location": location,
                "processing_notes": {
                    "rule_based_emergency": rule_emergency,
                    "rule_based_urgency": rule_urgency,
                    "specialty_confidence": confidence
                }
            }
            
            logger.info(
                f"Assessment complete: urgency={result['urgency_level']}, "
                f"emergency={result['emergency_flag']}, "
                f"specialty={result['recommended_specialty']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in assessment pipeline: {e}", exc_info=True)
            # Return safe fallback response
            return {
                "symptoms_identified": [],
                "urgency_level": "medium",
                "emergency_flag": False,
                "recommended_specialty": "General Physician",
                "care_setting": "clinic",
                "reasoning": "Unable to complete assessment. Please consult a healthcare professional for evaluation.",
                "safety_advice": "If you're experiencing severe symptoms, seek immediate medical attention.",
                "session_id": session_id,
                "user_input": user_message,
                "error": str(e)
            }
    
    def get_health_disclaimer(self) -> str:
        """
        Get medical disclaimer text
        
        Returns:
            Disclaimer text
        """
        return (
            "⚠️ IMPORTANT MEDICAL DISCLAIMER:\n"
            "This system provides care navigation guidance only and is NOT a substitute for professional medical advice, "
            "diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any "
            "questions you may have regarding a medical condition. Never disregard professional medical advice or delay "
            "seeking it because of information provided by this system. "
            "If you think you may have a medical emergency, call your doctor or emergency services immediately."
        )


# Create singleton instance
agent_orchestrator = AgentOrchestrator()
