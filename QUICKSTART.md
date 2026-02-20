# QUICK START GUIDE

## WHAT'S BEEN CREATED FOR YOU ✅

```
backend/
├── __init__.py
├── schemas.py                    ✅ Data contracts (TypedDict)
├── orchestrator.py               ✅ Integration template
├── agents/
│   ├── __init__.py
│   └── symptom_agent.py          ✅ MAIN AGENT - Ready to use!
└── utils/
    ├── __init__.py
    └── voice_utils.py            ✅ STT, TTS, image utilities

REQUIREMENTS.md                    ✅ What you need to build
ARCHITECTURE_ANALYSIS.md           ✅ Detailed technical analysis
```

---

## 3 SIMPLE STEPS TO RUN

### Step 1: Test Symptom Agent ✅ (NOW)

```bash
cd c:\Users\PARTH\OneDrive\Desktop\ai-doctor-2.0-voice-and-vision

# Run the agent directly
python -m backend.agents.symptom_agent
```

**Expected Output:**
```json
{
  "specialty": "Cardiology",
  "urgency": "critical",
  "emergency_flag": true,
  "confidence": 0.92,
  "reasoning": "...",
  "key_findings": ["chest pain", "shortness of breath"],
  "recommended_next_steps": [...]
}
```

### Step 2: Test Orchestrator Template ✅ (NOW)

```bash
python backend/orchestrator.py
```

This will test the orchestrator with 3 sample cases:
1. Emergency (chest pain)
2. General (cough + fever)
3. Dermatology (rash)

### Step 3: Integrate With Your Agents ⏳ (WHEN READY)

When you get hospital recommender and cost estimator agents:

1. Open `backend/orchestrator.py`
2. Replace placeholder functions:
   - `call_hospital_recommender_agent()`
   - `call_cost_estimator_agent()`
3. Point them to your actual agent endpoints/functions
4. Done! Orchestrator will work

---

## DETAILED USAGE

### Use Symptom Agent in Python

```python
from backend.agents.symptom_agent import symptom_analysis_agent
import json

# Simple case
result = symptom_analysis_agent("fever and cough")
print(json.dumps(result, indent=2, default=str))

# With medical image
result = symptom_analysis_agent(
    symptoms="red rash on skin",
    image_path="/path/to/skin_image.jpg"
)
print(json.dumps(result, indent=2, default=str))

# With image data (already encoded)
result = symptom_analysis_agent(
    symptoms="swollen area",
    image_base64="data:image/jpeg;base64,iVBOR..."
)
```

### Use Voice Utilities

```python
from backend.utils.voice_utils import (
    transcribe_with_groq,
    text_to_speech_with_gtts,
    encode_image_to_base64
)

# Speech to text
text = transcribe_with_groq("audio_file.mp3")
print(text)

# Text to speech
audio_path = text_to_speech_with_gtts("Hello, this is your health guidance")
print(f"Audio saved to: {audio_path}")

# Image encoding
image_b64 = encode_image_to_base64("medical_image.jpg")
print(f"Encoded: {image_b64[:50]}...")
```

### Use Orchestrator

```python
import asyncio
from backend.orchestrator import healthcare_orchestrator

async def main():
    result = await healthcare_orchestrator(
        symptoms="chest pain and shortness of breath",
        location="Mumbai",
        image_base64=None
    )
    print(result)

asyncio.run(main())
```

---

## DATA CONTRACTS

All TypedDict schemas in `backend/schemas.py`:

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
    UrgencyLevel,
    validate_symptom_output,
    validate_urgency,
    validate_specialty
)
```

---

## WHAT YOUR AGENTS SHOULD RETURN

### Hospital Recommender Agent

**Input:**
```python
{
    "specialty": "Cardiology",
    "location": "Mumbai",
    "urgency": "critical"
}
```

**Output:**
```python
{
    "hospitals": [
        {
            "name": "KEM Hospital",
            "distance_km": 2.1,
            "rating": 4.7,
            "cost_level": "high",
            "insurance_supported": True,
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
    "guidance": "These are top-rated hospitals...",
    "confidence": 0.85
}
```

### Cost Estimator Agent

**Input:**
```python
{
    "specialty": "Cardiology",
    "urgency": "critical",
    "location": "Mumbai"
}
```

**Output:**
```python
{
    "estimate": "₹800–₹2000",
    "confidence": 0.75,
    "breakdown": {
        "consultation": 500,
        "ecg": 500,
        "blood_tests": 1000
    }
}
```

---

## TESTING CHECKLIST

- [ ] Run symptom agent: `python -m backend.agents.symptom_agent`
- [ ] Run orchestrator: `python backend/orchestrator.py`
- [ ] Test with custom symptoms
- [ ] Test with medical image
- [ ] Verify JSON output format
- [ ] Check confidence scores
- [ ] Validate emergency detection

---

## ENVIRONMENT SETUP

**Required:**
```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
```

**Already installed (from current project):**
- groq
- gtts
- pydub
- pyaudio
- pillow
- python-dotenv

**You might need (if not installed):**
```bash
pip install pydantic typing-extensions
```

---

## FILE LOCATIONS

| File | Purpose |
|---|---|
| backend/schemas.py | TypedDict contracts |
| backend/agents/symptom_agent.py | Medical logic (you use) |
| backend/utils/voice_utils.py | STT/TTS helpers |
| backend/orchestrator.py | Integration template |
| REQUIREMENTS.md | What agents should return |
| ARCHITECTURE_ANALYSIS.md | Technical deep-dive |

---

## NEXT STEPS

### Stage 1: Understand ✅ (NOW)
- Read this file
- Run symptom agent test
- Review schemas.py
- Check orchestrator.py template

### Stage 2: Integration ⏳ (WHEN AGENTS READY)
- Get hospital recommender agent
- Get cost estimator agent
- Update orchestrator.py with their endpoints
- Test end-to-end

### Stage 3: Voice UI ⏳ (FINAL)
- Build frontend/voice_interface.py
- Connect to orchestrator
- Deploy

---

## SAFETY FEATURES Built-In ✅

1. **Emergency keyword detection** - Hardcoded, overrides LLM
2. **Output validation** - JSON schema enforcement
3. **Diagnosis prevention** - Blocked medical claims
4. **Confidence scoring** - Uncertainty quantification
5. **Graceful fallbacks** - Error handling
6. **Controlled vocabulary** - Enum-based classification

---

## QUESTIONS?

- **How to use symptom agent?** → See "Simple case" above
- **What should my agents return?** → See "Data Contracts" section
- **How to integrate orchestrator?** → See backend/orchestrator.py
- **What are the safety guardrails?** → See schemas.py and symptom_agent.py

---

## FINAL CHECKLIST BEFORE USING

- [ ] .env file has GROQ_API_KEY
- [ ] Ran `python -m backend.agents.symptom_agent`
- [ ] Reviewed backend/schemas.py
- [ ] Reviewed REQUIREMENTS.md
- [ ] Ready to get hospital + cost agents
