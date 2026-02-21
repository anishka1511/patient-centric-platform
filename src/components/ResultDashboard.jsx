import UrgencyBanner from './UrgencyBanner';
import DoctorList from './DoctorList';
import CostPanel from './CostPanel';
import HospitalMap from './HospitalMap';
import '../styles/ResultDashboard.css';

export default function ResultDashboard({ result, symptoms, onBackClick }) {
  return (
    <div className="result-dashboard">
      <button className="back-button" onClick={onBackClick}>
        ← New Search
      </button>

      <UrgencyBanner
        urgency={result.urgency}
        emergency_flag={result.emergency_flag}
      />

      <div className="result-container">
        {symptoms && (
          <div className="symptoms-display">
            <h3 className="symptoms-title">Your Symptoms</h3>
            <p className="symptoms-text">{symptoms}</p>
          </div>
        )}

        <div className="recommendation-section">
          <h2 className="recommendation-title">Recommendation</h2>
          <p className="recommendation-text">{result.recommendation}</p>
          <p className="specialty-info">Specialty: {result.specialty}</p>
        </div>

        {result.hospitals && result.hospitals.length > 0 && (
          <HospitalMap hospitals={result.hospitals} user_location={result.user_location} />
        )}

        <DoctorList hospitals={result.hospitals} specialty={result.specialty} />

        <CostPanel cost_estimate={result.cost_estimate} />
      </div>
    </div>
  );
}
