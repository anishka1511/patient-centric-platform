"""
Agent Orchestration Service
Coordinates the full symptom assessment pipeline
"""
from typing import Dict, Optional
from services.llm_service import llm_service
from utils.emergency_rules import emergency_detector
from utils.specialty_mapper import specialty_mapper
from config.logging_config import logger


class AgentOrchestrator:
    """
    Orchestrates the full symptom assessment workflow:
    1. Extract keywords from user input
    2. Detect emergency (rules + LLM)
    3. Assess symptoms
    4. Map to specialty
    5. Return structured response
    """
    
    def __init__(self):
        self.llm_service = llm_service
        self.emergency_detector = emergency_detector
        self.specialty_mapper = specialty_mapper
    
    def assess_user_input(self, user_message: str, session_id: Optional[str] = None) -> Dict:
        """
        Full assessment pipeline for user input
        
        Args:
            user_message: User's symptom description
            session_id: Optional session ID for conversation tracking
            
        Returns:
            Complete assessment result as dict
        """
        logger.info(f"Starting assessment for message: '{user_message[:50]}...'")
        
        try:
            # Step 1: Extract symptoms using LLM
            extraction_result = self.llm_service.extract_symptoms(user_message)
            symptoms = extraction_result.get("symptoms", [])
            logger.info(f"Extracted {len(symptoms)} symptoms")
            
            # Step 2: Rule-based emergency detection (safety net)
            rule_emergency, pattern, reason = self.emergency_detector.detect_emergency(
                user_message, symptoms
            )
            rule_urgency = self.emergency_detector.assess_urgency(user_message, symptoms)
            
            if rule_emergency:
                logger.warning(f"Emergency detected by rules: {reason}")
            
            # Step 3: LLM assessment
            llm_assessment = self.llm_service.assess_symptoms(symptoms)
            
            # Step 4: Override with rule-based detection if more severe
            if rule_emergency and not llm_assessment.get("emergency_flag"):
                logger.warning("Overriding LLM assessment - rules detected emergency")
                llm_assessment["emergency_flag"] = True
                llm_assessment["urgency_level"] = "high"
                llm_assessment["safety_advice"] = (
                    "URGENT: Seek immediate medical attention or go to the nearest emergency department. "
                    f"Detected: {reason}"
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
