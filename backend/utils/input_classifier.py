"""
Input Classification Service
Validates and categorizes user input before medical processing
"""
import re
from typing import Dict, List, Tuple
from backend.config.logging_config import logger

# Optional: RapidFuzz for typo tolerance (graceful degradation if not installed)
try:
    from rapidfuzz import fuzz
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    logger.warning("RapidFuzz not installed - typo detection disabled. Run: pip install rapidfuzz")


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
        "face numb", "arm numb", "half body weak", "drooping", "face is drooping",
        "arm feels weak", "arm weakness", "weak arm",
        
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
    
    # Vague symptoms that need more context when standalone
    VAGUE_SYMPTOMS = ['pain', 'ache', 'hurt', 'sick', 'ill', 'unwell', 'bad', 'feel', 'feeling']
    
    # Body parts
    BODY_PARTS = [
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

    # Known medical-intent terms where users may provide specialist/procedure/diagnosis
    # directly instead of symptom descriptions.
    KNOWN_MEDICAL_INTENT_TERMS = [
        # Specialists
        'dentist', 'dental', 'cardiologist', 'cardiology', 'dermatologist',
        'ent specialist', 'orthopedic', 'gynecologist', 'gastroenterologist',
        'neurologist', 'ophthalmologist', 'pulmonologist', 'urologist',
        'endocrinologist', 'psychiatrist', 'oncologist', 'nephrologist',
        'pediatrician', 'general physician', 'general doctor', 'primary care',
        # Procedures / interventions
        'tooth filling', 'root canal', 'dental filling', 'dental extraction',
        'wisdom tooth', 'dental surgery', 'angioplasty', 'bypass surgery',
        'brain surgery', 'appendectomy', 'biopsy', 'chemotherapy', 'radiation therapy',
        'dialysis', 'cataract surgery', 'orthopedic surgery',
        # Common diagnosis/conditions
        'cardiac arrest', 'heart attack', 'migraine', 'asthma', 'diabetes',
        'thyroid', 'pneumonia', 'depression', 'anxiety', 'kidney stone',
        'tooth decay', 'cavity', 'gingivitis',
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

        # PRIORITY 1.5: Known specialist/procedure/diagnosis should be actionable
        # even when users do not provide symptom-style wording.
        known_medical_term = self._extract_known_medical_term(user_input_lower)
        if known_medical_term:
            logger.info(f"Known medical-intent term detected: {known_medical_term}")
            return (
                "VALID_MEDICAL",
                f"Known medical term identified: {known_medical_term}",
                []
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
        words = set(user_input_lower.split())
        
        # Check if input is too vague (single symptom word without details)
        has_vague_only = any(vague in user_input_lower for vague in self.VAGUE_SYMPTOMS)
        has_body_part = any(part in user_input_lower for part in self.BODY_PARTS)
        has_specific_symptom = any(keyword in user_input_lower for keyword in 
            ['headache', 'fever', 'cough', 'nausea', 'vomiting', 'diarrhea', 'rash', 'migraine'])

        # Single body-part mentions (e.g. "head", "chest") need clarification.
        if has_body_part and not has_specific_symptom and not has_context and word_count <= 3:
            logger.info("Body part without symptom detail - needs more detail")
            primary = next((part for part in self.BODY_PARTS if part in user_input_lower), "this area")
            return (
                "INSUFFICIENT_INFO",
                "Body part mentioned without specific symptom",
                [
                    f"What is wrong with your {primary}?",
                    "Do you have pain, injury, swelling, or another issue?",
                    "When did it start?"
                ]
            )
        
        # If ONLY vague symptoms without body parts, context, or specific symptoms
        if has_vague_only and not has_body_part and not has_context and not has_specific_symptom and word_count <= 4:
            logger.info("Vague symptom detected - needs more detail")
            return (
                "INSUFFICIENT_INFO",
                "Symptom mentioned but lacks detail",
                [
                    "Where is the symptom located?",
                    "How long have you had this symptom?",
                    "How severe is it? (mild/moderate/severe)",
                    "Are there any other symptoms?"
                ]
            )
        
        # ANY medical symptom with some detail is valid - let triage agent handle full assessment
        # Per safety-first principle: don't block valid symptoms
        # Examples: "fever", "cough", "headache", "stomach pain"
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
        """
        Check if input contains emergency keywords using fuzzy matching
        Handles typos, misspellings, and variations
        Threshold: 85% similarity (catches most typos while avoiding false positives)
        """
        text_lower = text.lower()
        
        # First pass: Exact substring matching (always works)
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                return True, f"Emergency keyword detected: '{keyword}'"
        
        # Check for combined stroke symptoms (multiple indicators)
        stroke_indicators = ['droop', 'weak', 'numb', 'paralyz', 'slurred']
        body_parts = ['face', 'arm', 'leg', 'speech']
        stroke_count = sum(1 for indicator in stroke_indicators if indicator in text_lower)
        body_part_count = sum(1 for part in body_parts if part in text_lower)
        
        # If multiple stroke symptoms mentioned together -> emergency
        if stroke_count >= 2 or (stroke_count >= 1 and body_part_count >= 1):
            return True, f"Emergency: Multiple stroke symptoms detected"
        
        # Second pass: Fuzzy matching for typos (if rapidfuzz installed)
        if not FUZZY_MATCHING_AVAILABLE:
            return False, ""
        
        # Split text into words and phrases for matching
        words = text_lower.split()
        
        # Check single words and 2-word phrases
        for i in range(len(words)):
            # Single word
            word = words[i]
            for keyword in self.EMERGENCY_KEYWORDS:
                # Only do fuzzy match on keywords without spaces (single words)
                if ' ' not in keyword and len(word) >= 4 and len(keyword) >= 4:
                    similarity = fuzz.ratio(word, keyword)
                    if similarity >= 85:
                        logger.warning(f"Fuzzy emergency match: '{word}' ~= '{keyword}' ({similarity}%)")
                        return True, f"Emergency keyword detected (typo): '{word}' → '{keyword}'"
            
            # Two-word phrases
            if i < len(words) - 1:
                phrase = f"{words[i]} {words[i+1]}"
                for keyword in self.EMERGENCY_KEYWORDS:
                    if ' ' in keyword and len(phrase) >= 8:
                        similarity = fuzz.ratio(phrase, keyword)
                        if similarity >= 85:
                            logger.warning(f"Fuzzy emergency match: '{phrase}' ~= '{keyword}' ({similarity}%)")
                            return True, f"Emergency keyword detected (typo): '{phrase}' → '{keyword}'"
        
        return False, ""
    
    def _check_irrelevant(self, text: str) -> Tuple[bool, str]:
        """Check if input is non-medical/irrelevant"""
        for pattern in self.IRRELEVANT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Non-medical/social conversation detected"
        return False, ""
    
    def _has_medical_keywords(self, text: str) -> bool:
        """Check if text contains medical keywords"""
        return any(keyword in text for keyword in self.MEDICAL_KEYWORDS) or self._has_known_medical_intent(text)

    def _has_known_medical_intent(self, text: str) -> bool:
        """Check for specialist/procedure/diagnosis intent terms."""
        return any(term in text for term in self.KNOWN_MEDICAL_INTENT_TERMS)
    
    def _has_context(self, text: str) -> bool:
        """Check if text contains contextual details"""
        return any(indicator in text for indicator in self.CONTEXT_INDICATORS)
    
    def _extract_primary_symptom(self, text: str) -> str:
        """Extract the main symptom mentioned"""
        for keyword in self.MEDICAL_KEYWORDS:
            if keyword in text:
                return keyword
        return "symptom"

    def _extract_known_medical_term(self, text: str) -> str:
        """Return first matched known medical-intent term, if any."""
        for term in self.KNOWN_MEDICAL_INTENT_TERMS:
            if term in text:
                return term
        return ""


# Create singleton instance
input_classifier = InputClassifier()
