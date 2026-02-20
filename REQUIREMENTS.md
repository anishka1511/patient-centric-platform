# REQUIREMENTS: SYMPTOM AGENT INTEGRATION

## WHAT YOU NEED TO BUILD/PROVIDE

### 1. Symptom Analysis Agent ✅ (DONE - in backend/agents/symptom_agent.py)

**Status**: Fully implemented and ready to use

**Function Signature:**
```python
def symptom_analysis_agent(
    symptoms: str,
    image_base64: Optional[str] = None,
    image_path: Optional[str] = None,
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
) -> SymptomAgentOutput
```

**Input Format:**
```python
{
    "symptoms": "chest pain for 2 hours",
    "image_base64": "base64_encoded_image_or_none",  # Optional
    "image_path": "/path/to/image.jpg"  # Optional
}
```

**Output Format (STRICT JSON):**
```python
{
    "specialty": "Cardiology",  # MedicalSpecialty enum
    "urgency": "critical",  # UrgencyLevel enum
    "emergency_flag": true,
    "confidence": 0.92,  # 0.0-1.0
    "reasoning": "High-risk symptoms suggest cardiology consultation",
    "key_findings": ["chest pain", "shortness of breath"],
    "recommended_next_steps": [
        "Call emergency services immediately",
        "...more steps"
    ]
}
```

**Ready To Use:**
```python
from backend.agents.symptom_agent import symptom_analysis_agent

result = symptom_analysis_agent(
    symptoms="chest pain and difficulty breathing",
    image_path="/path/to/medical_image.jpg"
)
print(result)
```

---

### 2. Hospital Recommender Agent ⏳ (YOU WILL PROVIDE)

**Expected Input:**
```python
{
    "specialty": MedicalSpecialty,  # From symptom agent
    "location": str,  # "Mumbai", "Bangalore", etc.
    "urgency": UrgencyLevel  # From symptom agent
}
```

**Expected Output:**
```python
{
    "hospitals": [
        {
            "name": "KEM Hospital",
            "distance_km": 2.1,
            "rating": 4.7,
            "cost_level": "high",  # low|medium|high
            "insurance_supported": true,
            "doctors": [
                {
                    "name": "Dr. Sumedh Kulkarni",
                    "experience_years": 12,
                    "floor": "4th Floor",
                    "availability": "Available Today"
                }
            ]
        }
    ],
    "guidance": "Here are top-rated hospitals for Cardiology...",
    "confidence": 0.85
}
```

**Schema Defined In:**
- `backend/schemas.py` - `HospitalRecommenderInput`, `HospitalInfo`, `HospitalRecommenderOutput`

---

### 3. Cost Estimator Agent ⏳ (YOU WILL PROVIDE)

**Expected Input:**
```python
{
    "specialty": MedicalSpecialty,  # From symptom agent
    "urgency": UrgencyLevel,  # From symptom agent
    "location": str  # Optional
}
```

**Expected Output:**
```python
{
    "estimate": "₹800–₹2000",
    "confidence": 0.75,
    "breakdown": {
        "consultation": 500,
        "tests": 1000,
        "procedures": 500
    }
}
```

**Schema Defined In:**
- `backend/schemas.py` - `CostEstimatorInput`, `CostEstimatorOutput`

---

### 4. Orchestrator ⏳ (YOU WILL PROVIDE)

**Function Signature:**
```python
async def healthcare_orchestrator(
    symptoms: str,
    location: str,
    image_base64: Optional[str] = None
) -> OrchestratorOutput
```

**What It Should Do:**
1. Call `symptom_analysis_agent(symptoms, image_base64)`
2. If emergency_flag=true → return immediately with emergency guidance
3. Otherwise, call hospital_recommender_agent and cost_estimator_agent
4. Combine results into final OrchestratorOutput
5. Return comprehensive healthcare guidance

**Expected Output:**
```python
{
    "recommendation": "Immediate cardiology consultation recommended",
    "urgency": "critical",
    "emergency_flag": true,
    "specialty": "Cardiology",
    "hospitals": [...],  # From hospital agent
    "cost_estimate": "₹800–₹2000",  # From cost agent
    "guidance": "...",
    "confidence_score": 0.87
}
```

**Which We Will Call From UI:**
```python
from backend.orchestrator import healthcare_orchestrator

result = await healthcare_orchestrator(
    symptoms="chest pain and shortness of breath",
    location="Mumbai",
    image_base64=encoded_image
)
```

---

### 5. Voice Interface (UI Adapter) ⏳ (YOU CAN BUILD)

**Location**: `frontend/voice_interface.py`

**Purpose**: Adapter between Gradio UI and backend agents

**Flow:**
```
User speaks/uploads in Gradio
    ↓
transcribe_with_groq() [STT]
    ↓
Call healthcare_orchestrator()
    ↓
text_to_speech_with_gtts() [TTS] (optional)
    ↓
Display results + play audio
```

**Example Implementation:**
```python
from backend.utils.voice_utils import transcribe_with_groq, text_to_speech_with_gtts
from backend.orchestrator import healthcare_orchestrator
import base64

async def voice_interaction(audio_filepath, image_filepath):
    # STT
    symptoms = transcribe_with_groq(audio_filepath)
    
    # Image encoding (if provided)
    image_base64 = None
    if image_filepath:
        from backend.utils.voice_utils import encode_image_to_base64
        image_base64 = encode_image_to_base64(image_filepath)
    
    # Call orchestrator
    analysis = await healthcare_orchestrator(
        symptoms=symptoms,
        location="Mumbai",  # Get from user
        image_base64=image_base64
    )
    
    # TTS (optional - return voice response)
    voice_response = text_to_speech_with_gtts(
        analysis["guidance"],
        output_filepath="response.mp3"
    )
    
    return {
        "structured_output": analysis,
        "voice_response": voice_response
    }
```

---

## INTEGRATION CHECKLIST

### Phase 1: Ready Now ✅
- [x] Data schemas (backend/schemas.py)
- [x] Symptom agent (backend/agents/symptom_agent.py)
- [x] Voice utilities (backend/utils/voice_utils.py)

### Phase 2: Waiting For ⏳
- [ ] Hospital Recommender Agent (you provide)
- [ ] Cost Estimator Agent (you provide)
- [ ] Orchestrator (you provide)

### Phase 3: Build UI Adapter
- [ ] Voice interface adapter (frontend/voice_interface.py)
- [ ] Connect to orchestrator
- [ ] Test end-to-end

---

## DATA CONTRACTS (TypedDict)

All schemas defined in `backend/schemas.py`:

```python
from backend.schemas import (
    SymptomAgentInput,
    SymptomAgentOutput,
    HospitalRecommenderInput,
    HospitalRecommenderOutput,
    CostEstimatorInput,
    CostEstimatorOutput,
    OrchestratorOutput,
    MedicalSpecialty,
    UrgencyLevel
)
```

---

## ENVIRONMENT VARIABLES

Required in `.env`:
```
GROQ_API_KEY=<your_groq_key>
```

---

## FILE STRUCTURE

```
backend/
├── agents/
│   └── symptom_agent.py          ✅ DONE
├── utils/
│   └── voice_utils.py            ✅ DONE
└── schemas.py                    ✅ DONE

frontend/
└── voice_interface.py            ⏳ Build this

orchestrator.py                   ⏳ You provide

.env                              ✅ Already exists
```

---

## NEXT STEPS

1. **NOW**: Test symptom agent
   ```bash
   python -c "
   from backend.agents.symptom_agent import symptom_analysis_agent
   result = symptom_analysis_agent('chest pain and fever')
   print(result)
   "
   ```

2. **WHEN READY**: Build hospital/cost agents
3. **WHEN READY**: Build orchestrator
4. **FINALLY**: Build voice interface

---

## TESTING SYMPTOM AGENT

```python
from backend.agents.symptom_agent import symptom_analysis_agent
import json

# Test case 1: Emergency
result = symptom_analysis_agent("chest pain, difficulty breathing")
print(json.dumps(result, indent=2, default=str))

# Test case 2: General
result = symptom_analysis_agent("red rash on arm for 3 days")
print(json.dumps(result, indent=2, default=str))

# Test case 3: With image
result = symptom_analysis_agent(
    "itchy skin",
    image_path="/path/to/skin_image.jpg"
)
print(json.dumps(result, indent=2, default=str))
```

---

## SAFETY GUARDRAILS IMPLEMENTED

✅ Emergency keyword detection (hardcoded)
✅ Diagnosis prevention (blocked terms)
✅ JSON validation
✅ Confidence scoring
✅ Graceful error handling
✅ Structured output enforcement

---

## QUESTIONS?

- Symptom agent input/output: Check `backend/schemas.py`
- How to call symptom agent: See examples above
- How to integrate with orchestrator: See integration examples
- How to test: Run test cases above
