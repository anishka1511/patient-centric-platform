"""
LLM Service - Unified interface for OpenAI and Mock LLM
Automatically falls back to mock service if OpenAI is unavailable
"""
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from config.logging_config import logger
from services.mock_llm_service import mock_llm_service


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
                        api_key=settings.groq_api_key,
                        base_url=settings.groq_base_url
                    )
                    logger.info(f"LLM Service initialized with Groq AI (model: {settings.openai_model})")
                elif settings.llm_provider.lower() == "grok":
                    self.client = OpenAI(
                        api_key=settings.groq_api_key,
                        base_url=settings.grok_base_url
                    )
                    logger.info(f"LLM Service initialized with Grok AI (model: {settings.openai_model})")
                else:
                    self.client = OpenAI(api_key=settings.groq_api_key)
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

    def _parse_json_response(self, response_text: str) -> Dict:
        cleaned = response_text.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fence_match:
            return json.loads(fence_match.group(1))

        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        raise json.JSONDecodeError("No JSON object found in model response", cleaned, 0)
    
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
            result = self._parse_json_response(response_text)
            logger.info(f"OpenAI extracted symptoms: {result}")
            return result
        except Exception as e:
            logger.error(f"OpenAI symptom extraction failed: {e}. Falling back to mock.")
            self.use_mock = True
            return mock_llm_service.extract_symptoms(user_message)
    
    def assess_symptoms(self, symptoms: List[str]) -> Dict:
        """
        Assess symptoms and provide care navigation
        
        Args:
            symptoms: List of extracted symptoms
            
        Returns:
            Dict with assessment results
        """
        logger.info(f"Assessing symptoms: {symptoms}")
        
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
Maintain a calm, neutral, non-alarming tone."""

        symptoms_text = ", ".join(symptoms) if symptoms else "No specific symptoms mentioned"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please assess these symptoms: {symptoms_text}"}
        ]
        
        try:
            response_text = self._call_openai(messages, max_tokens=500)
            # Parse JSON response
            result = self._parse_json_response(response_text)
            logger.info(f"OpenAI assessment: urgency={result['urgency_level']}, emergency={result['emergency_flag']}")
            return result
        except Exception as e:
            logger.error(f"OpenAI assessment failed: {e}. Falling back to mock.")
            self.use_mock = True
            return mock_llm_service.assess_symptoms(symptoms)


# Create singleton instance (will auto-detect OpenAI availability)
llm_service = LLMService()
