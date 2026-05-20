"""
LLM Service - Unified interface for OpenAI and Mock LLM
Automatically falls back to mock service if OpenAI is unavailable
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config.settings import settings
from backend.config.logging_config import logger
from backend.services.mock_llm_service import mock_llm_service
from backend.utils.input_classifier import input_classifier


class LLMService:
    """
    LLM Service that supports both OpenAI and Mock fallback
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize LLM service
        
        Args:
            use_mock: Force use of mock service (default: auto-detect)
        """
        self.use_mock = use_mock
        self.client = None
        
        if not use_mock:
            try:
                # Configure for Groq, Grok, or OpenAI
                if settings.llm_provider.lower() == "groq":
                    self.client = OpenAI(
                        api_key=settings.openai_api_key,
                        base_url=settings.groq_base_url
                    )
                    logger.info(f"LLM Service initialized with Groq AI (model: {settings.openai_model})")
                elif settings.llm_provider.lower() == "grok":
                    self.client = OpenAI(
                        api_key=settings.openai_api_key,
                        base_url=settings.grok_base_url
                    )
                    logger.info(f"LLM Service initialized with Grok AI (model: {settings.openai_model})")
                else:
                    self.client = OpenAI(api_key=settings.openai_api_key)
                    logger.info(f"LLM Service initialized with OpenAI (model: {settings.openai_model})")
            except Exception as e:
                logger.warning(f"LLM initialization failed: {e}. Using mock service.")
                self.use_mock = True
        
        if self.use_mock:
            logger.info("LLM Service initialized with Mock service")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_openai(self, messages: List[Dict], max_tokens: int = 500) -> str:
        """
        Call OpenAI API with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=settings.openai_temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def extract_symptoms(self, user_message: str) -> Dict:
        """
        Extract symptoms from user message
        
        Args:
            user_message: User's description of symptoms
            
        Returns:
            Dict with 'symptoms' list
        """
        logger.info(f"Extracting symptoms from: '{user_message[:50]}...'")
        
        if self.use_mock:
            result = mock_llm_service.extract_symptoms(user_message)
            logger.info(f"Mock extracted symptoms: {result}")
            return result
        
        # OpenAI prompt for symptom extraction
        system_prompt = """You are a medical symptom keyword extraction assistant.

Your task is to extract ONLY medically relevant symptoms or physical complaints from the user's message.

Ignore all non-medical content, including:
- Greetings or conversational filler
- Emotions or opinions
- Jokes or sarcasm
- Uncertainty phrases (e.g., "maybe", "I think", "not sure")
- Irrelevant personal details
- Requests for diagnosis
- Medical conclusions or disease names unless stated as symptoms

IMPORTANT RULES:
1. Extract symptoms, not diagnoses.
2. Normalize symptoms into clear medical phrases.
3. Combine duplicates into a single entry.
4. Keep output concise.
5. If no symptoms are present, return an empty list.
6. Do not infer symptoms not explicitly stated.
7. Do not provide explanations or advice.

Examples of valid symptoms:
- chest pain
- shortness of breath
- fever
- headache
- tooth pain
- skin rash
- nausea
- dizziness
- abdominal pain
- ear pain

OUTPUT FORMAT:
Return ONLY valid JSON in this format:
{
  "symptoms": ["symptom1", "symptom2"]
}

No additional text."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response_text = self._call_openai(messages, max_tokens=200)
            # Parse JSON response
            result = json.loads(response_text)
            logger.info(f"OpenAI extracted symptoms: {result}")
            return result
        except Exception as e:
            logger.error(f"OpenAI symptom extraction failed: {e}. Falling back to mock.")
            self.use_mock = True
            return mock_llm_service.extract_symptoms(user_message)
    
    def classify_input(self, user_message: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Classify user input into categories using LLM
        Combines classification + extraction in one call for efficiency
        
        Args:
            user_message: User's raw input text
            history: Optional conversation history for context (list of {role, content} dicts)
            
        Returns:
            Dict with category, symptoms, emergency flag, and guidance
        """
        logger.info(f"Classifying input with LLM: '{user_message[:50]}...'")
        if history:
            logger.info(f"Using conversation history with {len(history)} messages")        
        if self.use_mock:
            return self._classify_with_rules(user_message)
        
        system_prompt = """You are a medical input classifier and symptom extractor.

Analyze the user's message and determine:
1. Is it medical-related or just conversation?
2. Does it contain actionable symptom information?
3. Is it an emergency?
4. Extract any symptoms mentioned

CATEGORIES:
- IRRELEVANT: Greetings, small talk, non-medical content (e.g., "hi", "thanks", "bye")
- INSUFFICIENT_INFO: Medical but too vague, needs clarification (e.g., "pain", "sick", "mild", "severe", single-word adjectives without symptoms)
- VALID_MEDICAL: Clear symptom description, actionable (e.g., "headache 3 days", "fever", "cherry angioma", "mild headache")
- EMERGENCY: Life-threatening symptoms requiring immediate care

CRITICAL CLASSIFICATION RULES:
1. Single adjectives without symptoms = INSUFFICIENT_INFO
   Examples: "mild", "severe", "bad", "terrible", "painful" alone
2. Single vague words = INSUFFICIENT_INFO  
   Examples: "pain", "sick", "ill", "unwell" without location/context
3. Single body part words without symptom = INSUFFICIENT_INFO
   Examples: "head", "chest", "stomach", "back", "leg" without describing what's wrong
4. Specialist/procedure/diagnosis inputs are VALID_MEDICAL
   Examples: "dentist", "tooth filling", "cardiac arrest", "migraine diagnosis"
5. Only mark as VALID_MEDICAL if there's a SPECIFIC symptom or known medical term
   Examples: "headache", "fever", "rash", "cough", "toothache", "chest pain"

EMERGENCY INDICATORS:
- Chest pain, heart attack, difficulty breathing, stroke symptoms
- Severe bleeding, unconsciousness, seizures
- Suicidal thoughts, overdose, poisoning
- Severe trauma, choking

EXAMPLES (FOLLOW THESE EXACTLY):

Input: "hi"
Output: {"category": "IRRELEVANT", "symptoms": [], "emergency": false, "message": "I'm here to help with medical symptoms.", "reason": "Non-medical greeting"}

Input: "mild"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Severity word without specific symptom", "clarifying_questions": ["What symptom are you experiencing?", "Where do you feel this?", "How long have you had it?"]}

Input: "severe"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Severity word without specific symptom", "clarifying_questions": ["What is severe?", "What symptom are you describing?", "Where is this located?"]}

Input: "pain"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": ["pain"], "emergency": false, "message": "I need more details.", "reason": "Too vague - no location or context", "clarifying_questions": ["Where is the pain?", "How long have you had it?", "How severe is it?"]}

Input: "sick"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Too vague - no specific symptoms", "clarifying_questions": ["What specific symptoms are you experiencing?", "Do you have fever, pain, nausea, or other symptoms?", "How long have you felt this way?"]}

Input: "not feeling well"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Too vague", "clarifying_questions": ["What specific symptoms do you have?", "Any pain, fever, or discomfort?", "When did this start?"]}

Input: "head"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Body part mentioned without specific symptom", "clarifying_questions": ["What is wrong with your head?", "Do you have a headache, injury, or other issue?", "When did it start?"]}

Input: "chest"
Output: {"category": "INSUFFICIENT_INFO", "symptoms": [], "emergency": false, "message": "I need more details.", "reason": "Body part mentioned without specific symptom", "clarifying_questions": ["What are you feeling in your chest?", "Is it pain, discomfort, or something else?", "How long have you had this?"]}

Input: "headache"
Output: {"category": "VALID_MEDICAL", "symptoms": ["headache"], "emergency": false, "message": "Medical concern identified", "reason": "Specific symptom mentioned"}

Input: "dentist"
Output: {"category": "VALID_MEDICAL", "symptoms": ["dental concern"], "emergency": false, "message": "Medical concern identified", "reason": "Specialist request is actionable"}

Input: "tooth filling"
Output: {"category": "VALID_MEDICAL", "symptoms": ["tooth filling"], "emergency": false, "message": "Medical concern identified", "reason": "Procedure request is actionable"}

Input: "mild headache"
Output: {"category": "VALID_MEDICAL", "symptoms": ["mild headache"], "emergency": false, "message": "Medical concern identified", "reason": "Specific symptom with severity"}

Input: "cherry angioma"
Output: {"category": "VALID_MEDICAL", "symptoms": ["cherry angioma"], "emergency": false, "message": "Medical concern identified", "reason": "Specific skin condition"}

Input: "face pimple"
Output: {"category": "VALID_MEDICAL", "symptoms": ["facial acne"], "emergency": false, "message": "Medical concern identified", "reason": "Dermatological symptom"}

Input: "chest pain cant breathe"
Output: {"category": "EMERGENCY", "symptoms": ["chest pain", "difficulty breathing"], "emergency": true, "message": "URGENT: Seek immediate medical attention", "reason": "Life-threatening cardiac/respiratory symptoms"}

Input: "face drooping arm weak"
Output: {"category": "EMERGENCY", "symptoms": ["facial drooping", "arm weakness"], "emergency": true, "message": "URGENT: Possible stroke", "reason": "Stroke warning signs"}

OUTPUT FORMAT (JSON only):
{
  "category": "IRRELEVANT | INSUFFICIENT_INFO | VALID_MEDICAL | EMERGENCY",
  "symptoms": ["extracted symptom1", "symptom2"],
  "emergency": true/false,
  "message": "brief user message",
  "reason": "why this category",
  "clarifying_questions": ["q1", "q2"] (only if INSUFFICIENT_INFO)
}

CONVERSATION CONTEXT:
If previous conversation history is provided, use it to understand context and resolve ambiguities.
For example:
- If user previously said "chest pain" and now says "for 2 hours, severe", combine into "severe chest pain for 2 hours"
- If follow-up provides location, severity, or duration, combine with previous symptoms
- Maintain medical context across turns
"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": f"Classify and extract: {user_message}"})
        
        try:
            response_text = self._call_openai(messages, max_tokens=300)
            result = json.loads(response_text)
            logger.info(f"LLM classification: {result.get('category')} - {result.get('reason')}")
            return result
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self._classify_with_rules(user_message)

    def _classify_with_rules(self, user_message: str) -> Dict:
        """Deterministic fallback classification when LLM is unavailable."""
        category, reason, prompts = input_classifier.classify_input(user_message)
        normalized = user_message.strip().lower()

        response = {
            "category": category,
            "symptoms": [] if category in ("IRRELEVANT", "INSUFFICIENT_INFO") else [user_message],
            "emergency": category == "EMERGENCY",
            "message": "I need more details." if category == "INSUFFICIENT_INFO" else "Processing your medical concern",
            "reason": reason,
        }

        if category == "IRRELEVANT":
            response["message"] = "I'm here to help with medical symptoms."

        if category == "INSUFFICIENT_INFO":
            response["clarifying_questions"] = prompts
        elif category == "EMERGENCY" and not response["symptoms"]:
            response["symptoms"] = [normalized]

        return response
    
    def assess_symptoms(self, symptoms: List[str], history: Optional[List[Dict]] = None) -> Dict:
        """
        Assess symptoms and provide care navigation
        
        Args:
            symptoms: List of extracted symptoms
            history: Optional conversation history for additional context
            
        Returns:
            Dict with assessment results
        """
        logger.info(f"Assessing symptoms: {symptoms}")
        if history:
            logger.info(f"Using conversation history with {len(history)} messages")
        
        if self.use_mock:
            result = mock_llm_service.assess_symptoms(symptoms)
            logger.info(f"Mock assessment: urgency={result['urgency_level']}, emergency={result['emergency_flag']}")
            return result
        
        # OpenAI prompt for symptom assessment
        system_prompt = """You are a healthcare navigation assistant, not a medical doctor.

Your task is to analyze user-reported symptoms and provide NON-DIAGNOSTIC guidance about the appropriate type of medical care to seek.

IMPORTANT RULES:
1. DO NOT provide medical diagnosis.
2. DO NOT name specific diseases as conclusions.
3. DO NOT recommend medications or treatments.
4. DO NOT replace professional medical advice.
5. Focus only on care navigation and urgency assessment.
6. Be safety-first: if symptoms indicate potential danger, flag emergency.

Your responsibilities:
A) Identify main symptoms from user input.
B) Determine urgency level:
   - low (self-limited / routine care)
   - medium (medical visit recommended)
   - high (urgent evaluation needed)

C) Detect emergency warning signs:
   Flag emergency if symptoms suggest possible life-threatening conditions such as:
   - Chest pain with breathlessness
   - Severe breathing difficulty
   - Stroke symptoms (facial drooping, weakness, speech difficulty)
   - Loss of consciousness
   - Severe bleeding
   - Seizures
   - Sudden severe headache
   - Serious trauma
   - High fever in infants
   - Any rapidly worsening condition

D) Recommend appropriate medical specialty or care setting:
   Examples:
   - General Physician / Primary Care
   - Cardiologist
   - Dermatologist
   - Dentist
   - ENT Specialist
   - Orthopedic
   - Gynecologist
   - Emergency Department

E) Provide brief reasoning WITHOUT diagnosing.

OUTPUT FORMAT:
Return ONLY valid JSON in the following structure:
{
  "symptoms_identified": [list of key symptoms],
  "urgency_level": "low | medium | high",
  "emergency_flag": true | false,
  "recommended_specialty": "string",
  "care_setting": "clinic | specialist_visit | emergency_department",
  "reasoning": "short explanation for recommendation",
  "safety_advice": "clear safety message if needed"
}

If emergency_flag is true, safety_advice must instruct immediate medical attention.
If information is insufficient, choose the safest reasonable recommendation.
Maintain a calm, neutral, non-alarming tone.

CONVERSATION CONTEXT:
If previous conversation history is provided, use it to understand the full context of the patient's condition.
Consider details mentioned in earlier messages when making your assessment.
"""

        symptoms_text = ", ".join(symptoms) if symptoms else "No specific symptoms mentioned"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current assessment request
        messages.append({"role": "user", "content": f"Please assess these symptoms: {symptoms_text}"})
        
        try:
            response_text = self._call_openai(messages, max_tokens=500)
            # Parse JSON response
            result = json.loads(response_text)
            logger.info(f"OpenAI assessment: urgency={result['urgency_level']}, emergency={result['emergency_flag']}")
            return result
        except Exception as e:
            logger.error(f"OpenAI assessment failed: {e}. Falling back to mock.")
            self.use_mock = True
            return mock_llm_service.assess_symptoms(symptoms)


# Create singleton instance (will auto-detect OpenAI availability)
llm_service = LLMService()
