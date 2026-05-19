# Patient-Centric Platform

Production-oriented FastAPI backend for symptom assessment, urgency triage, care navigation, and downstream recommendation enrichment.

This repo currently contains **two backend flows**:

1. `POST /api/assess` (primary flow)
- LLM + rule-based symptom assessment
- conversation persistence
- optional geolocation
- scraping/recommendation enrichment (input + output JSON attached to response)

2. `POST /api/analyze` (secondary orchestrator flow)
- mock multi-agent hospital orchestration (triage, hospital ranking, cost/review scoring)

A built-in web UI (`/`) calls `/api/assess` and now displays:
- disease detection result fields
- scraping input JSON
- scraping output JSON

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [End-to-End Call Flow](#end-to-end-call-flow)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Contracts](#requestresponse-contracts)
5. [Fallback Matrix](#fallback-matrix)
6. [Data & Recommendation Engine](#data--recommendation-engine)
7. [Project Structure](#project-structure)
8. [Configuration](#configuration)
9. [Local Setup & Run](#local-setup--run)
10. [Frontend Behavior](#frontend-behavior)
11. [Troubleshooting](#troubleshooting)
12. [Known Gaps / Notes](#known-gaps--notes)

---

## System Architecture

### Primary Runtime Topology

- `main.py`
  - boots FastAPI
  - mounts static UI
  - registers routes:
    - `routers/agent_routes.py` (`/api/assess`, `/api/conversation/{session_id}`, `/api/disclaimer`)
    - `api/routes.py` (`/api/analyze`)

- `routers/agent_routes.py`
  - intake endpoint for symptom messages
  - conversation + message persistence
  - orchestrated assessment via `services/agent_orchestrator.py`
  - downstream scraping payload construction and enrichment

- `services/agent_orchestrator.py`
  - LLM classification
  - rule-based emergency override
  - LLM assessment
  - specialty mapping + care setting

- `services/llm_service.py`
  - provider setup (Groq/Grok/OpenAI via OpenAI SDK)
  - robust classification/assessment calls
  - fallback to deterministic rules + mock service

- `data_loader.py`
  - recommendation engine using CSV datasets
  - severity-based routing (`low|medium|high`)
  - doctors/hospitals ranking and fallback logic

- Persistence layer
  - SQLAlchemy models: `Conversation`, `Message`, `Assessment`
  - DB session dependency in `config/database.py`

### Secondary Orchestration Flow

- `api/routes.py` -> `backend/orchestrator/aggregator.py`
  - separate mock orchestrator API (`/api/analyze`)
  - triage + mock hospital list + cost + review signals

---

## End-to-End Call Flow

### Flow A: `/api/assess` (primary)

1. Client posts symptom text (+ optional location/session).
2. Route creates/loads conversation.
3. Location resolution:
   - use provided location, else
   - auto-detect via IP service chain.
4. User message is stored in DB (`messages.extra_data` includes location metadata).
5. `AgentOrchestrator.assess_user_input(...)` executes:
   - classify input (`IRRELEVANT | INSUFFICIENT_INFO | VALID_MEDICAL | EMERGENCY`)
   - emergency rule checks + urgency adjustment
   - symptom assessment
   - specialty map + care setting
6. Assessment saved to DB.
7. If assessment is actionable and has valid lat/lon/specialty:
   - build `scraping_input`
   - call `generate_recommendation_response(scraping_input)`
   - attach `scraping_recommendations`
8. Route returns unified response to frontend.

### Flow B: `/api/analyze` (secondary)

1. Client posts structured triage payload.
2. `run_orchestration(...)` runs mock agents:
   - symptom triage
   - hospital fetch
   - review intel enrichment
   - cost estimate
   - weighted ranking
3. Returns `AnalyzeResponse`.

---

## API Endpoints

### System

- `GET /health`
- `GET /api-info`
- `GET /` (serves `static/index.html`)
- `GET /docs`
- `GET /redoc`

### Symptom Assessment Router (`routers/agent_routes.py`)

- `POST /api/assess`
- `GET /api/conversation/{session_id}`
- `GET /api/disclaimer`

### Orchestrator Router (`api/routes.py`)

- `POST /api/analyze`

### Internal/Unwired Router

- `backend/api/recommendation_api.py` defines `POST /recommend`
- Not currently mounted in `main.py`.

---

## Request/Response Contracts

## `POST /api/assess`

### Request (`SymptomAssessmentRequest`)

```json
{
  "message": "headache for 2 days",
  "session_id": "session-123",
  "location": {
    "latitude": 18.532468,
    "longitude": 73.866979
  },
  "user_context": {}
}
```

### Response (`SymptomAssessmentResponse`)

Always includes core fields:

- `symptoms_identified: string[]`
- `urgency_level: string`
- `emergency_flag: boolean`
- `recommended_specialty: string`
- `care_setting: string`
- `reasoning: string`
- `safety_advice: string | null`
- `session_id: string | null`
- `user_location: object | null`
- `disclaimer: string`

Added enrichment fields:

- `scraping_input: object | null`
  - present only when input is actionable and valid for recommendation engine.
- `scraping_recommendations: object | null`
  - output returned by `data_loader.generate_recommendation_response(...)`

### Clarification / irrelevant behavior

For vague or non-medical input, the endpoint still returns a valid `SymptomAssessmentResponse` (not an error), with:

- low urgency / clarification specialty
- reasoning containing clarifying prompts or suggestions
- `scraping_input = null`
- `scraping_recommendations = null`

---

## `GET /api/conversation/{session_id}`

Returns persisted message and assessment history for the session.

---

## `POST /api/analyze`

### Request (`AnalyzeRequest`)

```json
{
  "patient_id": "p-123",
  "age": 30,
  "gender": "female",
  "symptoms": ["fever", "cough"],
  "city": "Pune",
  "insurance_provider": "star"
}
```

### Response (`AnalyzeResponse`)

- `triage`
  - `specialty`, `urgency_level`, `emergency`, `confidence`, `rationale`
- `recommended_action`
- `hospitals[]`
  - distance/rating/wait/insurance/review/rank/cost hints
- `cost_overview` (nullable)
- `meta`
  - mock usage, flow type, timestamp

---

## Fallback Matrix

### LLM provider and inference fallbacks

1. `LLMService` init:
- if provider client init fails -> `use_mock = True`

2. Input classification:
- if LLM classification call fails -> deterministic rule classifier (`utils/input_classifier.py`)

3. Symptom assessment:
- if LLM assessment call fails -> mock assessment (`services/mock_llm_service.py`)

4. Orchestrator hard failure:
- returns safe medium-urgency fallback assessment object

### Emergency safety fallbacks

- Rule engine (`utils/emergency_rules.py`) can override non-emergency LLM outputs.
- Rule urgency can raise final urgency if higher than LLM urgency.

### Geolocation fallbacks

- if user location provided -> use it
- else IP geolocation chain:
  1. ipinfo.io (if key)
  2. ipapi.co
  3. ip-api.com
- private/local IP -> default Mumbai coords

### Scraping enrichment fallbacks

- executed only when all required fields exist:
  - `severity`, `location.latitude`, `location.longitude`, `specialty`
- if missing -> `scraping_input = null`, `scraping_recommendations = null`
- if engine throws -> `scraping_recommendations.error` object returned, base assessment remains intact

### Recommendation engine (data_loader) fallbacks

- severity routing:
  - `high`: hospital-only strict emergency filtering
  - `medium`: hospital-first, doctor fallback
  - `low`: doctor-first, hospital fallback
- location matching:
  - exact area first, then `NEARBY_MAP`
- specialty fallback:
  - tries requested specialty, then general physician fallback paths

---

## Data & Recommendation Engine

Core file: `data_loader.py`

### Inputs expected by enrichment

```json
{
  "severity": "low|medium|high",
  "location": {"latitude": 18.532468, "longitude": 73.866979},
  "specialty": "general physician"
}
```

### Returned shape

Depends on severity and availability, but generally includes:

- `care_setting`
- `metadata` (query info, routing type, fallback flags)
- `recommended_hospitals` and/or `recommended_doctors`
- optional cost summaries and fallback details
- `error` in failure cases

### Data files

- `data/doctors_master_sheet.csv`
- `data/hospitals.csv`

---

## Project Structure

```text
.
├── main.py
├── api/
│   └── routes.py                     # /api/analyze
├── routers/
│   ├── agent_routes.py               # /api/assess + conversation + disclaimer
│   └── schemas.py                    # request/response models
├── services/
│   ├── agent_orchestrator.py
│   ├── llm_service.py
│   ├── mock_llm_service.py
│   ├── geolocation_service.py
│   ├── conversation_service.py
│   └── scraping_adapter.py
├── utils/
│   ├── input_classifier.py
│   ├── emergency_rules.py
│   └── specialty_mapper.py
├── backend/
│   ├── orchestrator/aggregator.py    # mock orchestration pipeline
│   ├── agents/                        # mock agents
│   └── api/recommendation_api.py     # not mounted currently
├── models/
│   ├── conversation.py
│   ├── message.py
│   └── assessment.py
├── config/
│   ├── settings.py
│   ├── database.py
│   └── logging_config.py
├── data_loader.py                     # scraping/recommendation engine
├── static/index.html                  # web UI
├── scripts/
│   ├── setup_database.py
│   ├── verify_database.py
│   ├── dev_macos.sh
│   └── dev_windows.ps1
├── .env.example
└── requirements.txt
```

---

## Configuration

Example env (`.env.example`):

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./healthcare_agent.db
API_PORT=8000
API_HOST=0.0.0.0
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:8000
MAX_REQUESTS_PER_MINUTE=10
```

Key settings in `config/settings.py`:

- LLM:
  - `OPENAI_API_KEY`
  - `LLM_PROVIDER` (`groq` default, also `grok`, `openai`)
  - `OPENAI_MODEL`
  - `GROQ_BASE_URL`, `GROK_BASE_URL`
- DB:
  - `DATABASE_URL`
- API:
  - `API_HOST`, `API_PORT`, `LOG_LEVEL`
- geolocation:
  - `IPINFO_API_KEY`
  - `ENABLE_AUTO_LOCATION`

---

## Local Setup & Run

## 1) Create venv and install

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Hosting (Production)

This project separates frontend (static SPA) and backend (FastAPI). Recommended deployment:

- Frontend: AWS Amplify (static hosting, CI/CD from your repo branch)
- Backend: Render (Web Service) or any Python host that supports `gunicorn`/`uvicorn`

High-level steps

1. Backend (Render)
   - Create a Render **Web Service** pointing to this repository and branch.
   - Build command: `pip install -r requirements.txt` (Render auto-installs when `requirements.txt` exists).
   - Start command (recommended):
     ```bash
     gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
     ```
     or
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - Health check: `/health`
   - Add environment variables in Render Dashboard: `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `ALLOWED_ORIGINS` (comma-separated), `LOG_LEVEL`, etc.
   - Provision a managed Postgres on Render (or AWS RDS) and set `DATABASE_URL` in the service env. Do NOT use local sqlite in production.
  - Optional Render flag: `SERVE_STATIC` (default `false`). Set `SERVE_STATIC=true` only if you want the backend to serve static UI from `static/` or `dist/`; otherwise keep it false so the backend serves APIs only and the frontend is hosted separately (recommended).

2. Frontend (Amplify)
   - Connect Amplify Console to the repo and branch.
   - Build settings: install `npm ci`, build `npm run build`.
   - Amplify serves `dist/` produced by Vite; set environment variable `VITE_API_BASE_URL` to your Render backend URL (e.g. `https://your-backend.onrender.com`).
   - Add a single-page app rewrite rule that rewrites all routes to `/index.html` (200 rewrite) so client-side routing works.

3. CORS & Domains
   - Add your Amplify domain (and any custom domains) to the backend `ALLOWED_ORIGINS` env var.
   - Frontend should use the absolute backend URL in production (set `VITE_API_BASE_URL`).

Repository hints

- Do commit:
  - `vite.config.js`, `src/services/api.js` (or any code/config changes)
  - `requirements.txt`, `package.json`, `package-lock.json`
  - Optional infra file `render.yaml` and `amplify.yml` for reproducible deploy settings
- Do NOT commit:
  - Any `.env` files, secret keys, or local DB files. Add values via Render/Amplify env UI.

Example `render.yaml` (optional)

```yaml
services:
  - type: web
    name: patient-centric-backend
    env: python
    plan: starter
    repo: https://github.com/<your-org>/<repo>
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
    autoDeploy: true
    healthCheckPath: /health
databases:
  - name: patient-centric-db
    databaseName: patient_centric
    plan: starter
```

Example Amplify `amplify.yml` (optional)

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

Deployment checklist

- Commit & push your code to a branch (include `render.yaml` / `amplify.yml` if you want infra-as-code).
- Configure Render service and set environment variables and Postgres `DATABASE_URL`.
- Configure Amplify, set `VITE_API_BASE_URL` to the Render service URL, add the SPA rewrite.
- Deploy and monitor logs; verify `https://<your-backend>.onrender.com/health` returns `200`.

If you want, I can add a `render.yaml` to this repo with your repo URL/branch filled in and update the README with exact values — tell me the repo path and branch to use and I'll commit it.

### Important dependency note

`data_loader.py` uses `pandas`. If your environment does not have it:

```bash
python3 -m pip install pandas
```

## 2) Configure env

### macOS / Linux

```bash
cp .env.example .env
# edit values in .env
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
# edit values in .env
```

## 3) Initialize DB

### macOS / Linux

```bash
python3 scripts/setup_database.py
```

### Windows (PowerShell)

```powershell
python scripts/setup_database.py
```

## 4) Run server

### macOS / Linux

```bash
python3 main.py
```

or

```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

or mac helper:

```bash
./scripts/dev_macos.sh
```

### Windows (PowerShell)

```powershell
python main.py
```

or Windows helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev_windows.ps1
```

---

## Frontend Behavior

`static/index.html` calls `POST /api/assess`.

For actionable cases, it now displays below disease detection results:

1. `Scraping Input (JSON)`
2. `Scraping Output (JSON)`

Both JSON blocks are scrollable and shown only when `scraping_input` is present.

---

## Troubleshooting

### 1) `/api/assess` works but no scraping JSON shown

Likely one of these:
- input classified as `INSUFFICIENT_INFO`/`IRRELEVANT`
- missing lat/lon in location
- missing/empty specialty mapping result

Check response fields:
- `scraping_input`
- `scraping_recommendations`

### 2) LLM errors / fallback behavior

If provider/model mismatch occurs, classification/assessment fallback chain is used.
Ensure:
- provider + model are compatible
- API key is valid

### 3) Health endpoint shows `degraded`

Current `/health` DB ping uses raw SQL string (`SELECT 1`) which can fail under SQLAlchemy 2.x execution rules.

### 4) Geolocation unavailable

- Browser/user denied geolocation
- IP geolocation provider failure
- private/local IP routes to default location

### 5) Recommendation results empty

- coordinates may map outside supported local dataset radius
- specialty may not exist in current CSV data
- high severity enforces stricter hospital filters

---

## Known Gaps / Notes

1. `backend/api/recommendation_api.py` exists but is not currently mounted in `main.py`.
2. `.env.example` DB path (`healthcare_agent.db`) may differ from local `.env` depending on your setup.
3. `fix_database_schema.py` targets `healthcare_agent.db`; align DB filename if you rely on that migration helper.
4. `TEMP_README.md` is present as an auxiliary doc artifact.

---

## Quick Endpoint Smoke Test

```bash
curl -X POST http://127.0.0.1:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "message": "headache for 2 days",
    "session_id": "smoke-1",
    "location": {"latitude": 18.532468, "longitude": 73.866979}
  }'
```

Expect:
- core assessment fields
- `scraping_input` (non-null)
- `scraping_recommendations` (non-null/error object)

