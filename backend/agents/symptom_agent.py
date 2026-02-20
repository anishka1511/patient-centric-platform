"""
SYMPTOM ANALYSIS AGENT

Core medical logic agent that:
1. Analyzes symptoms and images
2. Classifies into medical specialties
3. Detects emergency situations
4. Returns structured JSON

This agent:
- Does NOT make diagnosis
- Returns routing guidance only
- Includes safety guardrails
- Ready to integrate with orchestrator
"""

import json
import os
import logging
from typing import Optional
from groq import Groq

from backend.schemas import (
    SymptomAgentInput,
    SymptomAgentOutput,
    UrgencyLevel,
    MedicalSpecialty,
    validate_symptom_output,
)

logger = logging.getLogger(__name__)

# ============================================================================
# EMERGENCY KEYWORD DETECTION (Guardrail 1)
# ============================================================================

EMERGENCY_KEYWORDS = {
    "chest pain", "difficulty breathing", "chest pressure", "shortness of breath",
    "severe headache", "sudden headache", "loss of consciousness", "unconscious",
    "severe bleeding", "bleeding uncontrolled", "can't swallow", "difficulty swallowing",
    "sudden paralysis", "paralyzed", "severe burns", "burn", "choking",
    "poisoning", "poison", "severe allergic", "anaphylaxis", "severe trauma",
    "broken bone severe", "spinal injury", "head injury", "drowning",
    "electric shock", "electrocution"
}

def detect_emergency_keywords(symptoms: str) -> bool:
    """Check if symptoms contain emergency keywords"""
    symptoms_lower = symptoms.lower()
    return any(keyword in symptoms_lower for keyword in EMERGENCY_KEYWORDS)

# ============================================================================
# BLOCKED CLAIMS (Guardrail 2)
# ============================================================================

BLOCKED_DIAGNOSIS_TERMS = {
    "you have", "you are suffering", "you suffer from",
    "you are diseased", "diagnosis:",
    "treatment plan", "medication",
    "cure this", "cure your", "heal this",
    "i prescribe", "you should take"
}

def contains_blocked_terms(text: str) -> bool:
    """Check if text contains therapy/diagnosis claims"""
    text_lower = text.lower()
    return any(term in text_lower for term in BLOCKED_DIAGNOSIS_TERMS)

# ============================================================================
# SYSTEM PROMPT (Guardrail 3: Controlled behavior)
# ============================================================================

SYSTEM_PROMPT = """You are a medical TRIAGE ASSISTANT, NOT a doctor.

YOUR ROLE:
- Classify symptoms for ROUTING to correct specialty
- Provide GUIDANCE only, NOT diagnosis or treatment
- Assess URGENCY and EMERGENCY status
- Return ONLY valid JSON

DO NOT:
- Suggest treatments
- Make diagnosis
- Prescribe medication
- Say "you have [disease]"
- Go beyond information for routing

RETURN ONLY JSON (no markdown, no explanation):
{
    "specialty": "<primary_specialty>",
    "secondary_specialties": ["<specialty>"],
    "urgency_level": "<low|medium|high|critical>",
    "reasoning": "<why this classification>",
    "key_findings": ["<finding1>", "<finding2>"],
    "is_emergency": <true|false>
}

VALID SPECIALTIES:
Cardiology, Dermatology, Orthopedics, Neurology, 
Gastroenterology, Respiratory, General, Emergency, 
Pediatrics, Psychiatry, Oncology, ENT

EMERGENCY TRIGGER WORDS (force "critical" + emergency=true):
chest pain, difficulty breathing, loss of consciousness, 
severe bleeding, severe burns, choking, paralysis, poisoning
"""

# ============================================================================
# IMAGE ENCODING (from current brain_of_the_doctor.py)
# ============================================================================

def encode_image(image_path: str) -> Optional[str]:
    """Convert image file to base64"""
    try:
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.warning(f"Failed to encode image: {e}")
        return None

# ============================================================================
# MAIN AGENT FUNCTION
# ============================================================================

def symptom_analysis_agent(
    symptoms: str,
    image_base64: Optional[str] = None,
    image_path: Optional[str] = None,
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
) -> SymptomAgentOutput:
    """
    SYMPTOM ANALYSIS AGENT
    
    Input:
        - symptoms: Patient symptom description
        - image_base64: Medical image (base64 encoded)
        - image_path: Path to medical image (will be encoded if provided)
        - model: LLM model to use
    
    Output:
        - Structured JSON: specialty, urgency, emergency_flag, confidence, reasoning, key_findings
    
    Safety:
        - Emergency keyword detection
        - Blocked diagnosis terms
        - Confidence scoring
        - JSON validation
    """
    
    # GUARDRAIL 1: Emergency keyword detection (hardcoded, no LLM)
    # This overrides any LLM output
    has_emergency_keyword = detect_emergency_keywords(symptoms)
    
    # GUARDRAIL 2: Encode image if path provided
    if image_path and not image_base64:
        image_base64 = encode_image(image_path)
    
    # Build user message
    user_message = f"Patient symptoms: {symptoms}"
    if image_base64:
        user_message += "\n[Medical image provided]"
    
    # STEP 1: Call LLM for medical analysis
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Build message with optional image
        message_content = [
            {"type": "text", "text": user_message}
        ]
        
        if image_base64:
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message_content}
            ],
            temperature=0.3,  # Low temperature for consistency
        )
        
        llm_output_str = response.choices[0].message.content
        logger.info(f"LLM output: {llm_output_str}")
        
        # STEP 2: Parse JSON response (handle markdown code blocks)
        try:
            # Clean markdown code blocks if present
            cleaned_output = llm_output_str
            if "```" in cleaned_output:
                # Extract JSON from markdown code block
                cleaned_output = cleaned_output.split("```")[1]
                if cleaned_output.startswith("json"):
                    cleaned_output = cleaned_output[4:]  # Remove 'json' language tag
                cleaned_output = cleaned_output.strip()
            
            llm_output = json.loads(cleaned_output)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from LLM: {llm_output_str}")
            # Fallback to generic emergency response
            llm_output = {
                "specialty": "General",
                "urgency_level": "medium",
                "reasoning": "Unable to analyze - refer to General practice",
                "key_findings": ["inconclusive"]
            }
        
        # STEP 3: Extract and validate fields
        specialty_str = llm_output.get("specialty", "General")
        urgency_str = llm_output.get("urgency_level", "medium").lower()
        reasoning = llm_output.get("reasoning", "")
        key_findings = llm_output.get("key_findings", [])
        is_emergency_llm = llm_output.get("is_emergency", False)
        
        # Map specialty to enum
        try:
            specialty = MedicalSpecialty(specialty_str)
        except ValueError:
            logger.warning(f"Invalid specialty from LLM: {specialty_str}")
            specialty = MedicalSpecialty.GENERAL
        
        # Map urgency to enum
        urgency_mapping = {
            "low": UrgencyLevel.LOW,
            "medium": UrgencyLevel.MEDIUM,
            "high": UrgencyLevel.HIGH,
            "critical": UrgencyLevel.CRITICAL
        }
        urgency = urgency_mapping.get(urgency_str, UrgencyLevel.MEDIUM)
        
        # STEP 4: Apply emergency override (Guardrail 1)
        # Emergency keywords override LLM output for safety
        if has_emergency_keyword:
            emergency_flag = True
            urgency = UrgencyLevel.CRITICAL
            specialty = MedicalSpecialty.EMERGENCY
            reasoning = f"EMERGENCY DETECTED: {symptoms[:50]}... Immediate medical attention required."
        else:
            emergency_flag = is_emergency_llm and urgency == UrgencyLevel.CRITICAL
        
        # STEP 5: Confidence scoring
        base_confidence = 0.85
        
        # Lower confidence if:
        # - Critical urgency (higher uncertainty)
        # - Few findings
        # - Blocked terms detected
        confidence_adjustments = []
        
        if urgency == UrgencyLevel.CRITICAL:
            confidence_adjustments.append(-0.15)  # Lower confidence for critical
        
        if len(key_findings) < 2:
            confidence_adjustments.append(-0.10)  # Low findings
        
        if contains_blocked_terms(reasoning):
            confidence_adjustments.append(-0.20)  # Suspicious wording
        
        confidence = base_confidence + sum(confidence_adjustments)
        confidence = max(0.4, min(1.0, confidence))  # Clamp 0.4-1.0
        
        # STEP 6: Recommended next steps
        if emergency_flag:
            recommended_next_steps = [
                "Call emergency services immediately (ambulance)",
                "Do not delay seeking care",
                "Inform paramedics of all symptoms"
            ]
        else:
            recommended_next_steps = [
                f"Schedule appointment with {specialty.value}",
                "Bring relevant medical records",
                "Note exact symptom onset time",
                "Visit nearest qualified clinic/hospital"
            ]
        
        # STEP 7: Build output
        output = SymptomAgentOutput(
            specialty=specialty,
            urgency=urgency,
            emergency_flag=emergency_flag,
            confidence=confidence,
            reasoning=reasoning,
            key_findings=key_findings if key_findings else ["symptoms analyzed"],
            recommended_next_steps=recommended_next_steps
        )
        
        # STEP 8: Validate output structure
        if not validate_symptom_output(output):
            logger.error("Invalid output structure from agent")
            # Return minimal valid output
            output = SymptomAgentOutput(
                specialty=MedicalSpecialty.GENERAL,
                urgency=UrgencyLevel.MEDIUM,
                emergency_flag=False,
                confidence=0.5,
                reasoning="Analysis inconclusive - refer to general practice",
                key_findings=["inconclusive"],
                recommended_next_steps=["Visit nearest clinic"]
            )
        
        logger.info(f"Agent output: {json.dumps(output, indent=2, default=str)}")
        return output
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        # Graceful fallback
        return SymptomAgentOutput(
            specialty=MedicalSpecialty.GENERAL,
            urgency=UrgencyLevel.MEDIUM,
            emergency_flag=False,
            confidence=0.3,
            reasoning=f"Error analyzing symptoms: {str(e)}",
            key_findings=[],
            recommended_next_steps=["Consult healthcare provider"]
        )

# ============================================================================
# TESTING (Remove before production)
# ============================================================================

if __name__ == "__main__":
    # Test emergency detection
    test_cases = [
        "chest pain for 2 hours",
        "red rash on arm",
        "difficulty breathing and chest pressure",
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test}")
        result = symptom_analysis_agent(test)
        print(json.dumps(result, indent=2, default=str))
