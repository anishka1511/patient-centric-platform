# Medical Guidance Orchestrator (Mock MVP)

This project started as an empty folder structure. We built a **working backend MVP** that takes patient symptom input and returns:
- symptom triage (how serious it is),
- hospital suggestions,
- estimated treatment cost,
- review-based insights,
- and a final ranked recommendation list.

Everything currently runs on **mock agents** (sample logic + sample data), so your teammate APIs are not required yet.

---

## What we built from scratch

### 1) API App Setup
- Created a FastAPI app in `main.py`.
- Added health check endpoint: `GET /health`.
- Added analysis endpoint: `POST /api/analyze`.

### 2) Request and Response Contracts
- Created JSON schema files:
  - `schemas/analyze-request.schema.json`
  - `schemas/analyze-response.schema.json`
- Added matching Pydantic models in `api/routes.py` for runtime validation.

### 3) Mock Agents
Implemented these files under `backend/agents/`:
- `mock_symptom_agent.py` → detects specialty, urgency, emergency flag.
- `mock_hospital_agent.py` → returns city/specialty-based hospitals.
- `mock_cost_agent.py` → returns cost range + breakdown.
- `mock_review_agent.py` → returns sentiment + hidden-charge risk.

### 4) Orchestrator / Aggregator Logic
In `backend/orchestrator/aggregator.py`, we built the main flow:
1. Read input symptoms.
2. Run symptom triage.
3. If emergency: return urgent path + nearest emergency-capable hospital(s).
4. If non-emergency: fetch hospitals + cost + review insights.
5. Rank hospitals with weighted score using:
   - rating,
   - distance,
   - affordability,
   - review score.
6. Return one combined structured response.

### 5) Basic Reliability
- Added structured 500 handling in API route.
- Added deterministic mock logic so outputs are testable and stable.

### 6) Dependencies
- Added `requirements.txt` with:
  - `fastapi`
  - `uvicorn`

---

## Current project flow (easy view)

User input -> API (`/api/analyze`) -> Orchestrator -> 4 mock agents -> Aggregated + Ranked response

---

## How to run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start server:

```bash
uvicorn main:app --reload
```

3. Open Swagger docs:

- http://127.0.0.1:8000/docs

4. Test endpoint:
- `POST /api/analyze`

---

## Sample request

```json
{
  "age": 30,
  "symptoms": ["fever", "cough"],
  "city": "Pune",
  "insurance_provider": "star"
}
```

---

## What is ready now

- End-to-end mock backend works.
- Emergency and non-emergency flows both work.
- Ranking is included.
- Contracts are defined separately in schema files.

---

## What to do next (recommended)

1. Freeze final team contract fields.
2. Replace each mock agent with real teammate service calls.
3. Keep orchestrator logic unchanged (swap only agent internals/imports).
4. Add unit tests for triage branch, emergency branch, and ranking output.
5. Add auth/logging/timeout/retry as production hardening.
