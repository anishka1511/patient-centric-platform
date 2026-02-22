import UrgencyBanner from './UrgencyBanner';
import DoctorList from './DoctorList';
import CostPanel from './CostPanel';
import HospitalMap from './HospitalMap';
import HospitalList from './HospitalList';
import '../styles/ResultDashboard.css';

const formatLocation = (location) => {
  if (!location) return 'Not detected';

  if (location.city) {
    const parts = [location.city, location.state || location.country].filter(Boolean);
    return parts.join(', ');
  }

  if (location.latitude != null && location.longitude != null) {
    return `${location.latitude}, ${location.longitude}`;
  }

  return 'Not detected';
};

export default function ResultDashboard({ result, symptoms, onBackClick }) {
  const normalizedUrgency = String(result?.urgency || '').toLowerCase();
  const showHospitalCards =
    Boolean(result?.emergency_flag) ||
    normalizedUrgency === 'high' ||
    normalizedUrgency === 'medium';

  const symptomsIdentified =
    result.symptoms_identified && result.symptoms_identified.length > 0
      ? result.symptoms_identified.join(', ')
      : 'None identified';

  return (
    <div className="result-dashboard">
      <UrgencyBanner urgency={result.urgency} emergency_flag={result.emergency_flag} />
      <button className="back-button" onClick={onBackClick}>
        New Search
      </button>

      <div className="result-container">
        {symptoms && (
          <div className="symptoms-display">
            <h3 className="symptoms-title">Your Symptoms</h3>
            <p className="symptoms-text">{symptoms}</p>
          </div>
        )}

        <div className="recommendation-section">
          <h2 className="recommendation-title">Assessment Results</h2>
          <p className="recommendation-text">{result.recommendation}</p>

          <div className="result-grid">
            <div className="result-row">
              <span className="label">Symptoms Identified</span>
              <span className="value">{symptomsIdentified}</span>
            </div>
            <div className="result-row">
              <span className="label">Urgency Level</span>
              <span className="value">{result.urgency.toUpperCase()}</span>
            </div>
            <div className="result-row">
              <span className="label">Recommended Specialty</span>
              <span className="value">{result.specialty}</span>
            </div>
            <div className="result-row">
              <span className="label">Care Setting</span>
              <span className="value">{String(result.care_setting || 'clinic').toUpperCase()}</span>
            </div>
            <div className="result-row">
              <span className="label">Session ID</span>
              <span className="value">{result.session_id || 'N/A'}</span>
            </div>
            <div className="result-row">
              <span className="label">Your Location</span>
              <span className="value">{formatLocation(result.user_location)}</span>
            </div>
          </div>
        </div>

        {result.safety_advice && (
          <div className="safety-advice-card">
            <h3>Safety Advice</h3>
            <p>{result.safety_advice}</p>
          </div>
        )}

        {showHospitalCards && (
          <HospitalList hospitals={result.hospitals || []} specialty={result.specialty} />
        )}

        <HospitalMap hospitals={result.hospitals || []} user_location={result.user_location} />

        <DoctorList
          hospitals={result.hospitals}
          doctors={result.doctors}
          specialty={result.specialty}
          user_location={result.user_location}
        />

        <CostPanel cost_estimate={result.cost_estimate} />

        {result.disclaimer && (
          <div className="disclaimer-card">
            <h3>Medical Disclaimer</h3>
            <p>{result.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
