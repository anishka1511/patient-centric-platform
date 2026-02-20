"""
Input Classification Service
Validates and categorizes user input before medical processing
"""
import re
from typing import Dict, List, Tuple
from config.logging_config import logger


class InputClassifier:
    """
    Classifies user input into categories:
    - IRRELEVANT: Greetings, small talk, non-medical content
    - INSUFFICIENT_INFO: Too vague, needs more details
    - EMERGENCY: Life-threatening symptoms (immediate triage)
    - VALID_MEDICAL: Actionable symptom description
    """
    
    # Emergency keywords - Simple substring matching (more forgiving)
    # Catches typos, colloquial language, informal speech
    EMERGENCY_KEYWORDS = [
        # Breathing emergencies
        "can't breathe", "cant breathe", "cannot breathe", "can t breathe",
        "difficulty breathing", "trouble breathing", "breathing difficulty",
        "shortness of breath", "short of breath", "choking", "gasping",
        "breathing issues", "breathing problem",
        
        # Chest/cardiac
        "chest pain", "chest hurt", "heart pain", "heart attack",
        "crushing pain", "pressure in chest", "tight chest", "cardiac",
        "heart hurting", "chest pressure",
        
        # Stroke symptoms
        "stroke", "face drooping", "face droop", "arm weakness", "arm weak",
        "slurred speech", "can't move arm", "cant move", "paralysis", "paralyzed",
        "face numb", "arm numb", "half body weak",
        
        # Severe bleeding
        "severe bleeding", "heavy bleeding", "blood loss", "bleeding bad",
        "won't stop bleeding", "wont stop bleeding", "hemorrhage",
        "bleeding heavily", "losing blood",
        
        # Loss of consciousness
        "unconscious", "passed out", "fainted", "blacked out",
        "unresponsive", "not responding", "loss of consciousness",
        "keep passing out", "dizzy and passing out",
        
        # Head trauma
        "severe head injury", "head trauma", "skull fracture", "hit head hard",
        "bad head injury", "major head injury",
        
        # Mental health emergency
        "want to die", "kill myself", "suicidal", "suicide", "end my life",
        "harm myself", "hurt myself", "don't want to live",
        
        # Overdose/poisoning
        "overdose", "overdosed", "took too many", "poisoning", "poison",
        "swallowed poison", "toxic", "ingested",
        
        # Seizures
        "seizure", "seizing", "convulsion", "convulsing", "shaking uncontrollably",
        "epileptic", "having seizure",
        
        # Severe burns
        "severe burn", "third degree", "major burn", "burned badly",
        
        # Other critical
        "severe pain", "worst pain", "unbearable pain",
        "passing out", "about to pass out", "feels like dying",
        "can't stand up", "collapsed",
    ]
    
    # Irrelevant patterns (non-medical)
    IRRELEVANT_PATTERNS = [
        r'^\s*(hi|hello|hey|good morning|good afternoon|good evening|good day).*[!.?]*\s*$',
        r'^\s*(thanks|thank you|thx|bye|goodbye|see you)\s*[!.?]*\s*$',
        r'^\s*(how are you|what\'s up|wassup)\s*[?!.]*\s*$',
        r'^\s*(nice|cool|okay|ok|alright)\s*[!.?]*\s*$',
        r'\b(have a (good|nice|great) day|take care)\b',
        r'\b(weather|sports|news|politics|movie)\b',
    ]
    
    # Medical keywords (valid input indicators)
    MEDICAL_KEYWORDS = [
        'pain', 'ache', 'hurt', 'sore', 'discomfort',
        'fever', 'temperature', 'chills', 'sweating',
        'nausea', 'vomiting', 'diarrhea', 'constipation',
        'headache', 'migraine', 'dizziness', 'dizzy', 'vertigo',
        'cough', 'coughing', 'congestion', 'runny nose', 'sore throat',
        'rash', 'itch', 'itching', 'swelling', 'bruise', 'cut',
        'fatigue', 'tired', 'weakness', 'exhausted',
        'anxiety', 'depressed', 'stress', 'insomnia',
        'bleeding', 'discharge', 'infection',
        'broken', 'fracture', 'sprain', 'injury',
        'symptom', 'sick', 'ill', 'unwell', 'feeling bad',
        'drooping', 'droop', 'weak', 'numb', 'paralyzed',
        # Body parts (for follow-up responses)
        'head', 'neck', 'back', 'spine', 'shoulder', 'arm', 'elbow', 'wrist', 'hand', 'finger',
        'chest', 'abdomen', 'stomach', 'belly', 'side', 'hip', 'leg', 'knee', 'ankle', 'foot', 'toe',
        'eye', 'ear', 'nose', 'mouth', 'throat', 'tooth', 'jaw',
        'heart', 'lung', 'kidney', 'liver', 'skin',
    ]
    
    # Context indicators (provide useful details)
    CONTEXT_INDICATORS = [
        'since', 'for', 'started', 'began', 'last',
        'days', 'hours', 'weeks', 'months',
        'severe', 'mild', 'moderate', 'intense',
        'constant', 'intermittent', 'occasional',
        'left', 'right', 'upper', 'lower', 'side',
    ]
    
    def classify_input(self, user_input: str) -> Tuple[str, str, List[str]]:
        """
        Classify user input and provide guidance
        
        Args:
            user_input: Raw user message
            
        Returns:
            Tuple of (category, reason, clarification_prompts)
            - category: EMERGENCY, VALID_MEDICAL, INSUFFICIENT_INFO, IRRELEVANT
            - reason: Explanation for classification
            - clarification_prompts: List of suggested questions (if needed)
        """
        user_input_lower = user_input.lower().strip()
        
        # Empty input
        if not user_input_lower or len(user_input_lower) < 2:
            return (
                "IRRELEVANT",
                "No meaningful input provided",
                ["Please describe your symptoms or health concern."]
            )
        
        # PRIORITY 1: Check for emergencies (must process immediately)
        is_emergency, emergency_reason = self._check_emergency(user_input_lower)
        if is_emergency:
            logger.warning(f"Emergency input detected: {emergency_reason}")
            return (
                "EMERGENCY",
                emergency_reason,
                []  # No clarification needed - immediate triage
            )
        
        # PRIORITY 2: Check for irrelevant/non-medical input
        is_irrelevant, irrelevant_reason = self._check_irrelevant(user_input_lower)
        if is_irrelevant:
            logger.info(f"Irrelevant input: {irrelevant_reason}")
            return (
                "IRRELEVANT",
                irrelevant_reason,
                [
                    "I'm here to help with medical symptom assessment.",
                    "Please describe any symptoms or health concerns you're experiencing."
                ]
            )
        
        # PRIORITY 3: Check if input has medical content
        has_medical_keywords = self._has_medical_keywords(user_input_lower)
        has_context = self._has_context(user_input_lower)
        
        if not has_medical_keywords:
            logger.info("No medical keywords detected")
            return (
                "INSUFFICIENT_INFO",
                "No clear medical symptoms mentioned",
                [
                    "Could you describe your specific symptoms?",
                    "What health concern would you like to discuss?",
                    "Examples: 'headache for 2 days', 'fever and cough', 'back pain'"
                ]
            )
        
        # PRIORITY 4: Check if medical input has sufficient detail
        word_count = len(user_input_lower.split())
        
        # ANY medical symptom is valid - let triage agent handle details
        # Per safety-first principle: don't block valid symptoms
        # Examples: "fever", "cough", "pain", "dizzy", "stomach pain"
        if has_medical_keywords:
            logger.info("Valid medical symptom detected")
            return (
                "VALID_MEDICAL",
                "Medical symptom identified - sufficient for assessment",
                []
            )
        
        # Fallback: No medical content detected
        logger.info("No actionable medical input")
        return (
            "INSUFFICIENT_INFO",
            "Unable to identify clear medical symptoms",
            [
                "Could you describe your symptoms in more detail?",
                "What specific health concern are you experiencing?"
            ]
        )
    
    def _check_emergency(self, text: str) -> Tuple[bool, str]:
        """Check if input contains emergency keywords - simple substring matching"""
        text_lower = text.lower()
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                return True, f"Emergency keyword detected: '{keyword}'"
        return False, ""
    
    def _check_irrelevant(self, text: str) -> Tuple[bool, str]:
        """Check if input is non-medical/irrelevant"""
        for pattern in self.IRRELEVANT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Non-medical/social conversation detected"
        return False, ""
    
    def _has_medical_keywords(self, text: str) -> bool:
        """Check if text contains medical keywords"""
        return any(keyword in text for keyword in self.MEDICAL_KEYWORDS)
    
    def _has_context(self, text: str) -> bool:
        """Check if text contains contextual details"""
        return any(indicator in text for indicator in self.CONTEXT_INDICATORS)
    
    def _extract_primary_symptom(self, text: str) -> str:
        """Extract the main symptom mentioned"""
        for keyword in self.MEDICAL_KEYWORDS:
            if keyword in text:
                return keyword
        return "symptom"


# Create singleton instance
input_classifier = InputClassifier()
