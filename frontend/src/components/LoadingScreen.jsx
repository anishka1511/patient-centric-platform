import { useState, useEffect } from 'react';
import '../styles/LoadingScreen.css';

const loadingMessages = [
  { text: 'Analyzing symptoms...', icon: '🔍', step: 1 },
  { text: 'Consulting AI models...', icon: '🧠', step: 2 },
  { text: 'Finding nearby hospitals...', icon: '🏥', step: 3 },
  { text: 'Gathering doctor profiles...', icon: '👨‍⚕️', step: 4 },
  { text: 'Estimating costs...', icon: '💰', step: 5 }
];

export default function LoadingScreen() {
  const [currentMessage, setCurrentMessage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % loadingMessages.length);
    }, 1400);

    return () => clearInterval(interval);
  }, []);

  const current = loadingMessages[currentMessage];

  return (
    <div className="loading-container">
      <div className="floating-orbs">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="loading-content">
        <div className="spinner-wrapper">
          <div className="spinner"></div>
          <div className="pulse-ring"></div>
        </div>

        <div className="loading-text-section">
          <p className="loading-icon">{current.icon}</p>
          <p className="loading-message">{current.text}</p>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${((current.step) / loadingMessages.length) * 100}%` }}
          ></div>
        </div>

        <p className="progress-text">Step {current.step} of {loadingMessages.length}</p>
      </div>
    </div>
  );
}
