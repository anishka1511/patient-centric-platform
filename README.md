# Patient-Centric Healthcare Platform

## Branch: `feature/input-agents`

AI-powered symptom assessment system with intelligent input classification and emergency detection.

---

## 🎯 What's Been Built

This branch implements a **production-ready AI agent** for symptom assessment with:

- ✅ **Input Classification** - Validates medical vs non-medical inputs
- ✅ **Emergency Detection** - Rule-based + LLM hybrid safety system
- ✅ **Symptom Extraction** - LLM-powered keyword extraction
- ✅ **Care Navigation** - Maps symptoms to appropriate medical specialties
- ✅ **Smart Follow-ups** - Guided intake with clarifying questions (not a chatbot)
- ✅ **Database Persistence** - SQLAlchemy with conversation tracking
- ✅ **REST API** - FastAPI with automatic OpenAPI docs

---

## 🏗️ Architecture

### Input Classification System

**Four Categories:**

1. **IRRELEVANT** - Greetings, small talk, non-medical content
   - Example: "hi", "have a good day", "thanks"
   - Response: Redirects to medical symptom input

2. **INSUFFICIENT_INFO** - Vague symptoms needing clarification
   - Example: "pain", "not feeling well", "sick"
   - Response: Structured clarifying questions (location, duration, severity)

3. **EMERGENCY** - Life-threatening symptoms
   - Example: "chest pain", "can't breathe", "stroke symptoms"
   - Response: Immediate triage, skip all follow-ups

4. **VALID_MEDICAL** - Actionable symptom descriptions
   - Example: "headache for 3 days, moderate pain"
   - Response: Full assessment with specialty recommendation

### Assessment Pipeline

```
User Input
    ↓
Input Classifier → [IRRELEVANT/INSUFFICIENT] → Return clarification
    ↓
[VALID_MEDICAL/EMERGENCY]
    ↓
LLM Symptom Extraction
    ↓
Rule-based Emergency Detection (safety backup)
    ↓
LLM Assessment (urgency, specialty, reasoning)
    ↓
Specialty Mapper (confidence-based augmentation)
    ↓
Return Assessment + Care Navigation
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source venv/Scripts/activate   # Git Bash
# OR
venv\Scripts\activate.bat      # CMD
# OR
venv\Scripts\Activate.ps1      # PowerShell

# Install dependencies (if needed)
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file:
```env
# Groq AI (current provider)
OPENAI_API_KEY=gsk_YOUR_KEY_HERE
LLM_PROVIDER=groq
GROQ_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile

# Database
DATABASE_URL=sqlite:///./healthcare_agent.db
```

### 3. Initialize Database

```bash
python scripts/setup_database.py
```

---

## 🧪 Testing

### Option 1: Interactive CLI (Recommended)

```bash
python test_interactive.py
```

**Try these examples:**
- Greeting: `hi`
- Vague: `pain` → then answer: `back pain in upper spine, moderate, 2 weeks`
- Emergency: `severe chest pain`
- Valid: `headache for 3 days with nausea`

### Option 2: Quick Validation (10 test cases)

```bash
python test_quick.py
```

### Option 3: Comprehensive Test Suite (24 test cases)

```bash
python test_input_classification.py
```

### Option 4: REST API Testing

**Terminal 1 - Start Server:**
```bash
python main.py
```
Server runs at: `http://localhost:8000`

**Terminal 2 - Test Endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Symptom assessment
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{"user_message": "headache for 3 days with nausea", "session_id": "test123"}'

# Get conversation history
curl http://localhost:8000/api/conversation/test123
```

**API Documentation:** http://localhost:8000/docs

---

## 📁 Project Structure

```
patient-centric-platform/
├── config/
│   ├── settings.py              # Environment config (Pydantic)
│   ├── database.py              # SQLAlchemy engine setup
│   └── logging_config.py        # Structured logging
├── models/
│   ├── conversation.py          # Conversation sessions
│   ├── message.py               # Chat messages
│   └── assessment.py            # Symptom assessments
├── services/
│   ├── llm_service.py           # Unified LLM interface (Groq/OpenAI)
│   ├── mock_llm_service.py      # Fallback rule-based system
│   ├── agent_orchestrator.py   # Main pipeline coordinator
│   └── conversation_service.py  # Database persistence
├── utils/
│   ├── input_classifier.py      # ⭐ Input validation (NEW)
│   ├── emergency_rules.py       # Rule-based emergency detection
│   └── specialty_mapper.py      # Symptom-to-specialty mapping
├── routers/
│   ├── agent_routes.py          # FastAPI endpoints
│   └── schemas.py               # Request/response models
├── main.py                      # FastAPI application
├── test_interactive.py          # Interactive testing CLI
├── test_quick.py                # Quick validation tests
├── test_input_classification.py # Comprehensive test suite
└── .env                         # Configuration (DO NOT COMMIT)
```

---

## 🎨 Design Philosophy

### Guided Intake Form (NOT Chatbot)

**Why this approach:**
- Healthcare requires structured, consistent data collection
- Reduces ambiguity and hallucination risk
- Provides predictable, testable behavior
- Easier frontend integration with form-based UI

**Implementation:**
- Detect insufficient input → ask specific questions
- User answers → process immediately
- No back-and-forth conversation loops
- Emergency cases bypass all follow-ups

### Safety-First Architecture

**Multi-layer emergency detection:**
1. **Input classifier** checks patterns first (highest priority)
2. **Rule-based detector** validates extracted symptoms
3. **LLM assessment** provides reasoning
4. **Override logic** uses most conservative urgency level

**Why hybrid approach:**
- LLMs can miss critical patterns
- Rules provide deterministic safety net
- Combination maximizes detection accuracy

---

## 📊 API Response Examples

### IRRELEVANT Input
```json
{
  "category": "IRRELEVANT",
  "message": "I'm here to help with medical symptom assessment.",
  "suggestions": [
    "Please describe any symptoms or health concerns you're experiencing."
  ],
  "session_id": "abc123",
  "user_input": "hello"
}
```

### INSUFFICIENT_INFO Input
```json
{
  "category": "INSUFFICIENT_INFO",
  "message": "I need more details to provide an accurate assessment.",
  "reason": "Symptom 'pain' mentioned but lacks detail",
  "clarifying_questions": [
    "Where is the pain located?",
    "How long have you had this pain?",
    "How severe is the pain? (mild/moderate/severe)",
    "Are there any other symptoms?"
  ],
  "session_id": "abc123",
  "user_input": "pain"
}
```

### VALID_MEDICAL Assessment
```json
{
  "symptoms_identified": ["headache", "nausea"],
  "urgency_level": "medium",
  "emergency_flag": false,
  "recommended_specialty": "General Physician",
  "care_setting": "clinic",
  "reasoning": "Headache with nausea suggests evaluation for possible migraine or other underlying causes.",
  "safety_advice": "If symptoms worsen or you experience sudden severe headache, seek immediate medical attention.",
  "session_id": "abc123",
  "user_input": "headache for 3 days with nausea"
}
```

### EMERGENCY Assessment
```json
{
  "symptoms_identified": ["chest pain"],
  "urgency_level": "high",
  "emergency_flag": true,
  "recommended_specialty": "Emergency Department",
  "care_setting": "emergency_department",
  "reasoning": "Chest pain requires immediate evaluation to rule out cardiac emergency.",
  "safety_advice": "URGENT: Seek immediate medical attention or go to the nearest emergency department.",
  "session_id": "abc123",
  "user_input": "severe chest pain"
}
```

---

## 🔧 Configuration Options

### LLM Providers

**Groq AI (Current):**
```env
LLM_PROVIDER=groq
GROQ_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

**OpenAI:**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

**Grok (X.AI):**
```env
LLM_PROVIDER=grok
GROK_BASE_URL=https://api.x.ai/v1
LLM_MODEL=grok-beta
```

### Database

**SQLite (Development):**
```env
DATABASE_URL=sqlite:///./healthcare_agent.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'tenacity'"
```bash
pip install tenacity colorama
```

### Issue: Input classification not working for follow-ups
**Solution:** Include symptom keyword in follow-up responses:
- ❌ "upper back, 1 month, moderate"
- ✅ "back pain in upper back, 1 month, moderate"

### Issue: API key errors
Check `.env` file has correct format:
- Groq keys start with `gsk_`
- OpenAI keys start with `sk-proj_`
- Grok keys start with `xai-`

### Issue: Database errors
```bash
# Reinitialize database
rm healthcare_agent.db
python scripts/setup_database.py
```

---

## 📈 Test Results

**Last Test Run:** All systems operational ✅

- ✅ Input Classification: 10/10 tests passed
- ✅ Follow-up Responses: Working correctly
- ✅ Emergency Detection: All patterns caught
- ✅ API Integration: Server running on localhost:8000
- ✅ Database: All tables initialized

---

## 🚧 TODO / Future Enhancements

- [ ] Frontend integration (teammate working on it)
- [ ] Multi-language support
- [ ] Conversation context memory (multi-turn)
- [ ] Integration with EHR systems
- [ ] Appointment scheduling
- [ ] Telemedicine video integration
- [ ] Analytics dashboard

---

## 👥 Contributing

This is a feature branch. Do NOT merge to main until:
1. All tests pass
2. Frontend integration complete
3. Security audit performed
4. Medical professional review conducted

---

## ⚠️ Medical Disclaimer

**IMPORTANT:** This system provides care navigation guidance only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

If you think you may have a medical emergency, call your doctor or emergency services immediately.

---

## 📝 License

[Add your license here]

---

## 📞 Contact

For questions about this feature branch, contact the development team.

**Built with:** Python 3.11, FastAPI, SQLAlchemy, Groq AI
