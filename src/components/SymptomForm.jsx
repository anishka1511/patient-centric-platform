import { useState, useRef, useEffect } from 'react';
import { getUserLocation } from '../services/geolocation';
import '../styles/SymptomForm.css';

export default function SymptomForm({ onSubmit }) {
  const [symptoms, setSymptoms] = useState('');
  const [location, setLocation] = useState('');
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speechError, setSpeechError] = useState('');
  const recognitionRef = useRef(null);
  const baseTranscriptRef = useRef('');

  useEffect(() => {
    // Initialize speech recognition if available
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        baseTranscriptRef.current = symptoms;
      };

      recognitionRef.current.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        // Update symptoms in real-time with both final and interim results
        const currentText = baseTranscriptRef.current + finalTranscript + interimTranscript;
        setSymptoms(currentText);

        // Update base transcript when we have final results
        if (finalTranscript) {
          baseTranscriptRef.current += finalTranscript;
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'no-speech') {
          setSpeechError('No speech detected. Please try again.');
        } else if (event.error === 'not-allowed') {
          setSpeechError('Microphone access denied. Please enable it in your browser settings.');
        } else {
          setSpeechError('Error occurred. Please try again.');
        }
        setTimeout(() => setSpeechError(''), 3000);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleVoiceInput = () => {
    if (!recognitionRef.current) {
      setSpeechError('Speech recognition is not supported in your browser.');
      setTimeout(() => setSpeechError(''), 3000);
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setSpeechError('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleUseCurrentLocation = async () => {
    setLocating(true);
    setLocationError('');
    
    try {
      const coords = await getUserLocation();
      setLocation(`[${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}]`);
    } catch (error) {
      setLocationError(error.message);
    } finally {
      setLocating(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (symptoms.trim() && location.trim()) {
      onSubmit({ symptoms, location });
      setSymptoms('');
      setLocation('');
    }
  };

  return (
    <form className="symptom-form" onSubmit={handleSubmit}>
      <h1 className="form-title">Healthcare Decision AI</h1>
      <p className="form-subtitle">Describe your symptoms and location to find nearby hospitals</p>

      <div className="form-group">
        <label htmlFor="symptoms">Describe Your Symptoms</label>
        <div className="symptoms-input-wrapper">
          <textarea
            id="symptoms"
            className="form-input textarea"
            placeholder="e.g., Fever, cough, body pain, headache..."
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            rows="5"
          ></textarea>
          <button 
            type="button"
            className={`voice-button ${isListening ? 'listening' : ''}`}
            onClick={handleVoiceInput}
            title={isListening ? 'Stop recording' : 'Start voice input'}
          >
            {isListening ? '🔴 Stop' : '🎤 Voice Input'}
          </button>
        </div>
        {speechError && <div className="speech-error">❌ {speechError}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="location">Your Location</label>
        <div className="location-input-wrapper">
          <input
            id="location"
            type="text"
            className="form-input"
            placeholder="e.g., Pune, Mumbai or Zip Code"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <button 
            type="button"
            className={`location-button ${locating ? 'loading' : ''}`}
            onClick={handleUseCurrentLocation}
            disabled={locating}
            title="Use your current location"
          >
            {locating ? '📍 Detecting...' : '📍 Use Current Location'}
          </button>
        </div>
        {locationError && <div className="location-error">❌ {locationError}</div>}
      </div>

      <button type="submit" className="submit-button">
        Analyze & Find Hospitals
      </button>
    </form>
  );
}
