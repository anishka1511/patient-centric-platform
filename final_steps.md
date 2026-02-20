# Final Steps: End-to-End Project Flow and Run Commands

## 1) What happens in this project (exact flow)

This project now supports a full HTTP flow:

1. **User sends symptom text** to `POST /api/assess`
2. **LLM agent (Groq/OpenAI-compatible service)** in `services/llm_service.py`:
   - Classifies input (`IRRELEVANT`, `INSUFFICIENT_INFO`, `VALID_MEDICAL`, `EMERGENCY`)
   - Extracts symptoms
3. **Agent orchestrator** in `services/agent_orchestrator.py`:
   - Applies emergency safety rules backup
   - Runs symptom assessment and urgency decision
   - Produces: symptoms, urgency, emergency flag, specialty, care setting
4. **Hospital/cost orchestration** via `POST /api/analyze` (`backend/orchestrator/aggregator.py`):
   - Triage for emergency/non-emergency
   - Hospital ranking (non-emergency flow)
   - Cost estimation summary
5. **Doctor recommendation** via `POST /api/recommend` (`backend/api/recommendation_api.py`):
   - Uses specialty + location
   - Returns recommended doctors and related metadata/cost summary

---

## 2) Run the program with `main.py`

## Prerequisites
- You are inside project folder
- Virtual environment exists at `.venv`
- Required env variables are set in `.env` (e.g., `GROQ_API_KEY`, `DATABASE_URL`, etc.)

## Start server
```bash
cd ~/Desktop/aissms
source .venv/Scripts/activate
python main.py
```

Server should run on `http://localhost:8000`.

Useful URLs:
- Swagger Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## 3) Pure HTTP full-chain test (no manual Python wiring)

Open another terminal and run:

```bash
cd ~/Desktop/aissms
source .venv/Scripts/activate
```

### Step A: LLM assessment
```bash
curl -s -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "message":"I have severe headache and fever for 3 days",
    "session_id":"final-chain-test"
  }' | cat
```

Check in response:
- `symptoms_identified`
- `urgency_level`
- `emergency_flag`
- `recommended_specialty`

### Step B: Orchestrator (hospitals + cost)
Use symptoms from Step A (example below):

```bash
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id":"final-chain-test",
    "age":30,
    "gender":"unknown",
    "symptoms":["severe headache","fever"],
    "city":"Mumbai",
    "insurance_provider":null
  }' | cat
```

Check in response:
- `triage` (includes emergency and urgency)
- `hospitals`
- `cost_overview`

### Step C: Doctor recommender
Use specialty from Step A (example below):

```bash
curl -s -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "specialty":"General Physician",
    "location":"Mumbai",
    "top_k":5
  }' | cat
```

Check in response:
- `recommended_doctors`
- `metadata`
- `cost_summary`

---

## 4) Optional quick checks

```bash
python test_imports.py
python test_quick.py
python test_llm_classification.py
python test_complete_system.py
python test_recommendations.py
bash test_api_bash.sh
```

---

## 5) Stop server
In the terminal where `python main.py` is running, press:

```bash
Ctrl + C
```
