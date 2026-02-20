# 🏥 AI Doctor 2.0 - Voice & Vision

**An intelligent medical diagnosis assistant powered by voice recognition, image analysis, and AI-driven symptom routing.**

> Transform patient descriptions and medical images into structured clinical assessments in real-time.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Architecture](#architecture)
8. [API Integration](#api-integration)
9. [Error Handling](#error-handling)
10. [Development](#development)
11. [Troubleshooting](#troubleshooting)
12. [Future Enhancements](#future-enhancements)
13. [License](#license)

---

## 🎯 Overview

**AI Doctor 2.0** is a comprehensive healthcare technology solution that combines:
- **Voice Processing** - Convert patient speech to medical text using Groq's Whisper API
- **Image Analysis** - Analyze medical images using multimodal LLMs
- **Medical Routing** - Classify symptoms by specialty and urgency level
- **Emergency Detection** - Identify critical cases in real-time
- **Voice Response** - Doctor's assessment delivered as audio feedback

### Use Cases
- 🏥 **Triage System** - Route patients to appropriate departments
- 📱 **Telehealth** - Remote symptom assessment and initial screening
- 🚑 **Emergency Response** - Rapid emergency detection and routing
- 📚 **Medical Education** - Learn diagnostic decision-making
- 🔍 **Image Diagnostics** - Analyze skin conditions, x-rays, wounds

---

## ✨ Features

### Core Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| **Voice Input** | ✅ | Microphone recording → Groq Whisper STT |
| **Text Output** | ✅ | Structured medical assessment |
| **Voice Output** | ✅ | Text-to-Speech response with autoplay |
| **Optional Images** | ✅ | Medical image upload (system works without) |
| **Image Validation** | ✅ | Blur detection, format checking, quality assurance |
| **Symptom Routing** | ✅ | 12+ medical specialties classification |
| **Urgency Levels** | ✅ | LOW, MEDIUM, HIGH, CRITICAL |
| **Emergency Alerts** | ✅ | Keyword-based detection system |
| **Minimal Symptom Guidance** | ✅ | Prompts users for more detail |
| **Error Recovery** | ✅ | Graceful fallbacks for all failures |

### Advanced Validation

```
Image Validation Pipeline:
├── File Format Check (JPEG, PNG, BMP, GIF)
├── Resolution Validation (min 100x100px)
├── File Size Check (>20KB)
├── Blur Detection (Laplacian variance)
└── Quality Assessment
```

---

## 📂 Project Structure

```
ai-doctor-2.0-voice-and-vision/
│
├── 🎨 Frontend (User Interface)
│   └── gradio_app.py                 # Main Gradio interface
│
├── 🧠 Core Processing
│   ├── brain_of_the_doctor.py        # Image analysis with Groq
│   ├── voice_of_the_patient.py       # Speech-to-text (Groq Whisper)
│   └── voice_of_the_doctor.py        # Text-to-speech (gTTS)
│
├── 🔧 Backend System
│   └── backend/
│       ├── agents/
│       │   ├── __init__.py
│       │   └── symptom_agent.py      # Medical triage & classification
│       ├── utils/
│       │   ├── __init__.py
│       │   └── voice_utils.py        # STT/TTS/Image validation
│       ├── orchestrator.py           # Multi-agent coordinator
│       ├── schemas.py                # Type contracts (TypedDict)
│       └── __init__.py
│
├── 📚 Documentation
│   ├── README.md                     # This file
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── REQUIREMENTS.md               # Data contracts & integration specs
│   └── test7README.md                # Legacy documentation
│
└── ⚙️ Configuration
    ├── .env                          # API keys (Git-ignored)
    ├── .gitignore                    # Git ignore rules
    └── requirements.txt              # Python dependencies
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** (Tested on 3.13)
- **Git**
- **FFmpeg** (for audio processing)
- **PortAudio** (for microphone input)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-doctor-2.0-voice-and-vision.git
cd ai-doctor-2.0-voice-and-vision
```

### Step 2: Create Python Environment

**Using venv:**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**Using conda:**
```bash
conda create -n ai-doctor python=3.11
conda activate ai-doctor
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install System Dependencies

**macOS:**
```bash
brew install ffmpeg portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y ffmpeg portaudio19-dev python3-pyaudio
```

**Windows:**
- Download FFmpeg: https://ffmpeg.org/download.html
- Download PortAudio: http://www.portaudio.com/download.html
- Add to PATH environment variable

### Step 5: Verify Installation

```bash
python -c "import gradio; import groq; import cv2; print('✅ All dependencies installed!')"
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Groq API (Required - for LLM, STT, multimodal image analysis)
GROQ_API_KEY=gsk_your_api_key_here

# ElevenLabs API (Optional - for premium text-to-speech)
ELEVEN_API_KEY=sk_your_api_key_here
```

### Obtaining API Keys

**Groq API (Free):**
1. Visit https://console.groq.com
2. Sign up for free account
3. Create API key
4. Set `GROQ_API_KEY` in `.env`

**ElevenLabs API (Optional):**
1. Visit https://elevenlabs.io
2. Create account
3. Generate API key
4. Set `ELEVEN_API_KEY` in `.env`

---

## 📖 Usage

### Quick Start

```bash
python gradio_app.py
```

The app will start on `http://127.0.0.1:7861`

### User Interface

```
┌─────────────────────────────────────────┐
│  AI Doctor with Vision and Voice        │
├─────────────────────────────────────────┤
│                                         │
│  📊 Record Your Symptoms (required)     │
│  [🎤 Click to record microphone]        │
│                                         │
│  📷 Medical Image (optional)            │
│  [📁 Choose file]                       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │         SUBMIT                  │   │
│  └─────────────────────────────────┘   │
│                                         │
├─────────────────────────── OUTPUT ──────┤
│  Your Symptoms (Transcribed)            │
│  Medical Assessment (Result)            │
│  Doctor's Voice Response (Audio)        │
└─────────────────────────────────────────┘
```

### Example Flows

#### Flow 1: Audio-Only (No Image)

```
User: "I have a fever and sore throat"
↓
[STT] Transcription: "I have a fever and sore throat"
↓
[Symptom Agent] Analysis
↓
RESULT: - 
Symptoms: I have a fever and sore throat
Urgency: MEDIUM
Emergency: NO
Specialty: RESPIRATORY
Care Setting: clinic
Reasoning: Symptoms suggest upper respiratory infection. Recommend consultation with respiratory specialist.
your location: longitude latitude

ℹ️ NOTE: For more accurate diagnosis, please provide more details...
↓
[TTS] Doctor's response as audio
```

#### Flow 2: Audio + Valid Medical Image

```
User: Records "I have a skin rash" + Uploads clear skin image
↓
[STT + Image Analysis] Multimodal processing
↓
[Groq Multimodal LLM] Analyzes image + symptoms together
↓
RESULT: [Doctor's detailed assessment based on image]
↓
[TTS] Audio response
```

#### Flow 3: Audio + Invalid Image

```
User: Records symptoms + Uploads blurry/wrong image
↓
[Image Validation] Detects blur score < threshold
↓
RESULT: - 
Symptoms: [user symptoms]
Urgency: N/A
Emergency: NO
Specialty: N/A
Care Setting: N/A
Reasoning: Invalid Image - Image is blurred. Please reupload a clear image.

⚠️ IMAGE ERROR: Image is blurred. Please reupload a clear image.
```

---

## 🏗️ Architecture

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
│  ┌──────────────┐      ┌──────────────────────────────┐   │
│  │ 🎤 Microphone│      │ 📷 Medical Image (Optional)  │   │
│  └──────┬───────┘      └──────────┬───────────────────┘   │
└─────────┼──────────────────────────┼─────────────────────────┘
          │                          │
          ▼                          │
    ┌──────────────┐                │
    │ Groq Whisper │ (STT)          │
    │ API          │                │
    └──────┬───────┘                │
           │ (transcribed_text)     │
           ▼                        ▼
    ┌────────────────────────────────────────┐
    │      IMAGE VALIDATION MODULE           │
    │  ┌──────────────────────────────────┐  │
    │  │ • Format check                   │  │
    │  │ • Resolution validation          │  │
    │  │ • Blur detection (Laplacian)     │  │
    │  │ • Quality assessment             │  │
    │  └──────────────────────────────────┘  │
    └───────────┬────────────────────────────┘
                │ (validation_result)
     ┌──────────┴─────────────┐
     │                        │
    VALID                   INVALID
     │                        │
     ▼                        ▼
┌──────────────┐      ┌──────────────────┐
│ Multimodal   │      │ Return Error     │
│ LLM Analysis │      │ Message &        │
│ (image+text) │      │ Reupload Prompt  │
└──────┬───────┘      └──────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ ROUTING DECISION                    │
│ ┌─────────────────────────────────┐ │
│ │ IF image NOT provided:          │ │
│ │   → Call Symptom Agent          │ │
│ │ ELSE:                           │ │
│ │   → Use Multimodal Analysis     │ │
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │
         ▼
    ┌──────────────────┐
    │ Symptom Agent    │
    │ • Emergency check│
    │ • Specialty route│
    │ • Urgency level  │
    │ • Recommendations│
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Format Result    │
    │ (RESULT: - ...) │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Add Guidance?    │
    │ (if minimal      │
    │  symptoms)       │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ gTTS Text-to-    │
    │ Speech           │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ OUTPUT LAYER     │
    │ • Text display   │
    │ • Audio playback │
    └──────────────────┘
```

### Component Details

#### 1. **Symptom Agent** (`backend/agents/symptom_agent.py`)

Classifies symptoms using Groq's Llama model with safety guardrails:

```python
Input:  symptoms (str), optional image_base64
Output: {
    "specialty": "Cardiology|Respiratory|...",
    "urgency": "LOW|MEDIUM|HIGH|CRITICAL",
    "emergency_flag": bool,
    "confidence": 0.0-1.0,
    "reasoning": str,
    "key_findings": [str],
    "recommended_next_steps": [str]
}
```

**Safety Features:**
- Emergency keyword detection (overrides LLM)
- Blocked diagnosis terms prevention
- Confidence scoring
- JSON validation

#### 2. **Voice Utilities** (`backend/utils/voice_utils.py`)

Speech and image processing:

```python
# Speech-to-Text
transcribe_with_groq(audio_filepath, GROQ_API_KEY)
→ transcribed_text

# Text-to-Speech
text_to_speech_with_gtts(input_text, output_filepath)
→ audio_file_path

# Image Validation
validate_image_before_analysis(image_path)
→ (is_valid: bool, error_message: str)

# Image Blur Detection
check_image_blur(image_path, threshold=100.0)
→ {"is_blurred": bool, "blur_score": float, "message": str}
```

#### 3. **Image Analysis** (`brain_of_the_doctor.py`)

Multimodal LLM analysis for images:

```python
analyze_image_with_query(
    query: str,          # User symptoms + system prompt
    encoded_image: str,  # Base64 encoded image
    model: str           # Groq model name
)
→ analysis_text
```

---

## 🔌 API Integration

### Required APIs

#### Groq API

**Endpoints Used:**
- `chat.completions.create()` - LLM inference (Llama models)
- `audio.transcriptions.create()` - Whisper STT

**Models:**
- LLM: `meta-llama/llama-4-scout-17b-16e-instruct` (multimodal)
- STT: `whisper-large-v3`

**Rate Limits:**
- Free tier: 6,000 requests/day
- Suitable for production with monitoring

#### ElevenLabs API (Optional)

**Endpoints:**
- `text_to_speech.convert()` - Premium text-to-speech

**Quality:** Premium natural voices
**Fallback:** Uses free gTTS if not configured

### Data Flow with APIs

```
Client Request
    ↓
[Groq Whisper] STT API
    ↓ (transcribed_text)
[Groq Llama] LLM API (Symptom Analysis)
    ↓ (analysis_result)
[gTTS or ElevenLabs] TTS API
    ↓ (audio_file)
Client Response
```

---

## ⚠️ Error Handling

### Multi-Layer Error Recovery

The application implements comprehensive error handling:

```python
try:
    # 1. Audio Transcription
    try:
        text = transcribe_with_groq(audio_path)
    except Exception as e:
        return "Error in recording"
        
    # 2. Image Processing (if provided)
    if image_provided:
        try:
            validate_image_before_analysis(image_path)
            analyze_image(image_path)
        except Exception as e:
            return user_friendly_error_message(e)
    
    # 3. Symptom Analysis
    try:
        result = symptom_analysis_agent(text)
    except Exception as e:
        return fallback_medical_routing(text)
    
    # 4. Text-to-Speech
    try:
        audio_path = text_to_speech(result)
    except Exception as e:
        return result_text_only(result)
        
except Exception as e:
    return system_error_response(e)
```

### Error Message Categories

1. **Image Errors:**
   - "Image is blurred. Please reupload a clear image."
   - "Image resolution too low. Please upload higher resolution."
   - "Invalid format: [format]. Please upload JPEG, PNG, or BMP."

2. **Audio Errors:**
   - "Error in recording. Please try again."
   - "Audio file not found or corrupted."

3. **Processing Errors:**
   - "Error in analysis. Please record symptoms again."
   - "System error. Please refresh and try again."

---

## 👨‍💻 Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone <repo>
cd ai-doctor-2.0-voice-and-vision
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Format code
black *.py backend/**/*.py

# Lint code
flake8 *.py backend/**/*.py

# Type checking
mypy --strict gradio_app.py
```

### Key Files to Modify

| File | Purpose | Modifications |
|------|---------|---------------|
| `gradio_app.py` | UI logic | Adjust output format, add features |
| `backend/agents/symptom_agent.py` | Medical routing | Update specialties, emergency keywords |
| `backend/utils/voice_utils.py` | Image validation | Tune blur threshold, adjust validations |
| `backend/schemas.py` | Data contracts | Add new medical specialties |

### Adding New Medical Specialties

1. Edit `backend/schemas.py`:
```python
class MedicalSpecialty(str, Enum):
    CARDIOLOGY = "Cardiology"
    NEUROLOGY = "Neurology"
    YOUR_NEW_SPECIALTY = "Your New Specialty"  # Add here
```

2. Update symptom keywords in `backend/agents/symptom_agent.py`

3. Test with new symptoms

### Creating Custom Models

Replace model in `gradio_app.py`:
```python
model="meta-llama/llama-4-scout-17b-16e-instruct"
# Try other Groq models:
# - llama-3.1-70b-versatile
# - mixtral-8x7b-32768
```

---

## 🔧 Troubleshooting

### Issue: "GROQ_API_KEY not found"

**Solution:**
```bash
# Create .env file with:
GROQ_API_KEY=your_key_here

# Or set environment variable:
export GROQ_API_KEY="your_key_here"  # Linux/Mac
set GROQ_API_KEY=your_key_here       # Windows
```

### Issue: Audio Playback Error on Windows

**Warning Message:**
```
Exception calling "PlaySync": "The file located at final.mp3 is not a valid wave file."
```

**Solution:**
This is a known PowerShell issue. Audio still works; only the playback notification fails.
- Audio is saved correctly to `final.mp3`
- Play manually if needed
- Or install alternative audio player

### Issue: "No module named 'cv2'"

**Solution:**
```bash
pip install opencv-python
```

### Issue: "Microphone not detected"

**Solutions:**
1. Check microphone permissions
2. Reinstall PyAudio:
   ```bash
   pip uninstall pyaudio
   pip install pyaudio
   ```
3. USB microphone issues - try restarting

### Issue: Image Validation Always Rejects Images

**Troubleshooting:**
```python
# Check blur threshold (in voice_utils.py):
check_image_blur(image_path, threshold=100.0)  # Increase threshold for lenient mode

# Check image resolution:
# Minimum: 100x100 pixels

# Check file format:
# Supported: JPEG, PNG, BMP, GIF
```

### Issue: High API Latency

**Solutions:**
1. Use lower temperature for faster responses:
   ```python
   temperature=0.3  # Already optimized
   ```

2. Cache frequent requests:
   ```python
   @functools.lru_cache(maxsize=100)
   def symptom_analysis_agent(...):
       ...
   ```

3. Monitor API usage on Groq dashboard

---

## 🚀 Future Enhancements

### Phase 2: Hospital Integration
- [ ] Integrate hospital recommender agent
- [ ] Real hospital database connection
- [ ] Doctor availability checking
- [ ] Booking system

### Phase 3: Cost & Insurance
- [ ] Cost estimator agent
- [ ] Insurance verification
- [ ] Payment integration

### Phase 4: Advanced Features
- [ ] Multi-language support (Spanish, Hindi, Arabic)
- [ ] Patient history tracking
- [ ] Medication interaction checker
- [ ] Medical records integration
- [ ] Integration with EHR systems

### Phase 5: Mobile & Deployment
- [ ] React Native mobile app
- [ ] Docker containerization
- [ ] AWS/GCP/Azure deployment
- [ ] API Gateway & Load balancing
- [ ] Admin dashboard

### Phase 6: Analytics & ML
- [ ] Usage analytics dashboard
- [ ] Fine-tuned medical models
- [ ] Feedback collection system
- [ ] Model performance monitoring

---

## 📊 Performance Metrics

### Typical Response Times

| Operation | Time | Device |
|-----------|------|--------|
| Audio recording (10s) | ~10s | Microphone |
| STT transcription | ~2-4s | Groq API |
| Image validation | ~0.5-1s | Local |
| Symptom analysis | ~3-5s | Groq API |
| Text-to-speech | ~1-2s | gTTS API |
| **Total** | **~7-15s** | - |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| Storage | 500MB | 1GB+ |
| CPU | 2 cores | 4+ cores |
| Internet | 1Mbps | 5Mbps+ |
| Python | 3.10 | 3.11+ |

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

- **Issues:** GitHub Issues
- **Documentation:** See QUICKSTART.md, REQUIREMENTS.md
- **Email:** [Your Email]
- **Website:** [Your Website]

---

## 🙏 Acknowledgments

- **Groq** - For powerful LLM and Whisper API
- **Gradio** - For intuitive UI framework
- **OpenCV** - For image processing
- **Google TTS** - For accessible text-to-speech

---

## 📝 Version History

- **v2.0.0** (Feb 2026) - Full release with voice, vision, and validation
- **v1.0.0** (Jan 2026) - Initial release with basic symptom analysis

---

**Last Updated:** February 21, 2026  
**Status:** ✅ Production Ready
