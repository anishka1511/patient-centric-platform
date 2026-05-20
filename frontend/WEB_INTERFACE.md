# Web Interface - Browser Geolocation

## 🌟 New Feature: Browser-Based Location Detection

The web interface now uses the **Browser Geolocation API** for accurate, GPS-based location detection.

## 🚀 Quick Start

### 1. Start the Server
```bash
python main.py
```

### 2. Open the Web Interface
Visit: **http://localhost:8000**

### 3. Grant Location Permission
- Your browser will ask: "Allow location access?"
- Click **"Allow"** for accurate location detection
- If denied, the system falls back to IP-based detection

## 🎯 How It Works

### Browser Geolocation Flow:
```
1. User opens webpage
2. Browser requests location permission
3. User clicks "Allow"
4. GPS coordinates obtained (lat/long)
5. Coordinates sent to backend API
6. Backend uses coordinates for hospital recommendations
```

### Location Priority:
1. **Browser GPS** (most accurate) - if permission granted
2. **IP-based detection** (fallback) - if permission denied
3. **Default Mumbai** (localhost fallback)

## 📱 Features

### ✅ What the Web Interface Provides:
- **Automatic location detection** with browser GPS
- **Real-time symptom assessment** with AI
- **Conversation history** across multiple messages
- **Emergency detection** with safety alerts
- **Specialty recommendations** based on symptoms
- **Location-based care navigation**

### 📍 Location Detection:
- **High Accuracy**: Uses device GPS when available
- **Privacy Focused**: Requires explicit user permission
- **Fallback Support**: Falls back to IP-based detection
- **Transparency**: Shows location source in results

## 🧪 Test Examples

### Example 1: Simple Symptom
```
Input: "headache for 3 days"
Result: 
- Symptoms: headache
- Urgency: Medium
- Specialty: General Physician
- Location: [Your GPS coordinates]
```

### Example 2: Multi-turn Conversation
```
Input 1: "chest pain"
Response: "How long? How severe?"

Input 2: "2 hours, severe, constant"
Response: [Emergency assessment with location]
```

### Example 3: Emergency
```
Input: "chest pain cant breathe"
Result:
- EMERGENCY FLAG: True
- Urgency: High
- Safety Advice: Seek immediate medical attention
- Location: [Your GPS coordinates]
```

## 🔧 Technical Details

### Frontend Code (JavaScript):
```javascript
// Request geolocation permission
navigator.geolocation.getCurrentPosition(
  (position) => {
    const location = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude
    };
    // Send to backend API
    sendToBackend(symptoms, location);
  },
  (error) => {
    // Permission denied - use IP fallback
    sendToBackend(symptoms, null);
  }
);
```

### Backend API Endpoint:
```
POST http://localhost:8000/api/assess
```

### Request Payload:
```json
{
  "message": "chest pain for 2 hours",
  "session_id": "session_12345",
  "location": {
    "latitude": 19.0760,
    "longitude": 72.8777
  }
}
```

### Response:
```json
{
  "symptoms_identified": ["chest pain"],
  "urgency_level": "high",
  "emergency_flag": true,
  "recommended_specialty": "Cardiologist",
  "care_setting": "emergency_department",
  "reasoning": "Chest pain requires immediate evaluation",
  "safety_advice": "Seek immediate medical attention",
  "user_location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "source": "user_provided"
  }
}
```

## 🔒 Privacy & Security

### Location Data:
- ✅ **User consent required** - Browser asks permission
- ✅ **Stored temporarily** - Only for session duration
- ✅ **Not shared** - Used only for care recommendations
- ✅ **Optional** - System works without location

### Best Practices:
1. Always ask for permission first
2. Explain why location is needed
3. Provide fallback options
4. Show location source to users

## 🛠️ Troubleshooting

### Location Not Detected:
- **Issue**: "Location permission denied"
- **Fix**: Click browser address bar lock icon → Allow location

### API Not Responding:
- **Issue**: "Failed to fetch"
- **Fix**: Make sure server is running: `python main.py`

### CORS Errors:
- **Issue**: Cross-origin blocked
- **Fix**: Already configured in main.py (no action needed)

## 📚 API Documentation

Visit: **http://localhost:8000/docs**

Interactive Swagger UI with:
- All API endpoints
- Request/response schemas
- Try-it-out functionality

## 🎨 Customization

### Modify Frontend:
Edit: `static/index.html`

### Modify Backend:
Edit: `routers/agent_routes.py`

### Location Service:
Edit: `services/geolocation_service.py`

## 🚀 Next Steps

### Future Enhancements:
- [ ] Hospital recommendations based on GPS coordinates
- [ ] Distance calculation to nearest hospitals
- [ ] Map view with hospital locations
- [ ] Save favorite locations
- [ ] Location history

### Integration Ideas:
- Mobile app integration
- Telemedicine video calls
- Appointment booking
- Medical records integration

## 📞 Support

For issues or questions:
1. Check the logs in console
2. Visit /docs for API documentation
3. Test with curl/Postman first
4. Enable browser developer tools

---

**Built with:**
- Frontend: HTML5 Geolocation API
- Backend: FastAPI + Python
- AI: Groq (Llama 3.3 70B)
- Database: SQLite

**Location Accuracy:**
- GPS: ±10 meters (browser geolocation)
- IP: ±10 kilometers (fallback)
