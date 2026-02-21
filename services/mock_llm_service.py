"""
Mock LLM Service for testing without OpenAI credits
This simulates OpenAI API responses so we can continue development
"""
import json
from typing import Dict, List


class MockLLMService:
    """Mock LLM service that simulates OpenAI responses"""
    
    def extract_symptoms(self, user_message: str) -> Dict:
        """
        Mock symptom extraction - simulates keyword extraction
        """
        user_lower = user_message.lower()
        
        # Simple keyword matching
        symptoms = []
        if "chest pain" in user_lower or "chest hurt" in user_lower:
            symptoms.append("chest pain")
        if "breath" in user_lower or "breathing" in user_lower:
            symptoms.append("shortness of breath")
        if "headache" in user_lower or "head hurt" in user_lower:
            symptoms.append("headache")
        if "fever" in user_lower or "temperature" in user_lower:
            symptoms.append("fever")
        if "cough" in user_lower:
            symptoms.append("cough")
        if "throat" in user_lower:
            symptoms.append("sore throat")
        if "stomach" in user_lower or "abdominal" in user_lower:
            symptoms.append("abdominal pain")
        if "nausea" in user_lower or "vomit" in user_lower:
            symptoms.append("nausea")
        if "dizzy" in user_lower or "dizziness" in user_lower:
            symptoms.append("dizziness")
        if "rash" in user_lower or "skin" in user_lower:
            symptoms.append("skin rash")
        
        return {"symptoms": symptoms}
    
    def assess_symptoms(self, symptoms: List[str]) -> Dict:
        """
        Mock symptom assessment - simulates healthcare navigation
        """
        # Emergency keywords
        emergency_keywords = ["chest pain", "shortness of breath", "severe bleeding", 
                            "unconscious", "stroke", "seizure"]
        
        # Check for emergency
        emergency_flag = any(symptom in emergency_keywords for symptom in symptoms)
        
        if emergency_flag:
            return {
                "symptoms_identified": symptoms,
                "urgency_level": "high",
                "emergency_flag": True,
                "recommended_specialty": "Emergency Medicine",
                "care_setting": "emergency_department",
                "reasoning": "Symptoms suggest a potentially serious condition requiring immediate evaluation.",
                "safety_advice": "Seek immediate medical attention or go to the nearest emergency department."
            }
        
        # Medium urgency
        medium_keywords = ["fever", "severe pain", "persistent cough", "headache"]
        if any(keyword in " ".join(symptoms) for keyword in medium_keywords):
            return {
                "symptoms_identified": symptoms,
                "urgency_level": "medium",
                "emergency_flag": False,
                "recommended_specialty": "General Physician",
                "care_setting": "clinic",
                "reasoning": "Symptoms warrant medical evaluation within 1-2 days.",
                "safety_advice": "Schedule an appointment with your primary care physician."
            }
        
        # Low urgency
        return {
            "symptoms_identified": symptoms,
            "urgency_level": "low",
            "emergency_flag": False,
            "recommended_specialty": "General Physician",
            "care_setting": "clinic",
            "reasoning": "Symptoms appear mild and may resolve on their own. Consider routine check-up if persisting.",
            "safety_advice": "Monitor symptoms. Seek care if condition worsens."
        }


# Create singleton instance
mock_llm_service = MockLLMService()
