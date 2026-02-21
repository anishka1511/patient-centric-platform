import HospitalCard from './HospitalCard';
import '../styles/HospitalList.css';

export default function HospitalList({ hospitals, specialty }) {
  if (!hospitals || hospitals.length === 0) {
    return (
      <div className="hospital-list">
        <div className="empty-state">
          <p>No nearby hospitals found for {specialty}.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="hospital-list">
      <h2 className="list-title">Nearby Hospitals</h2>
      <div className="hospital-grid">
        {hospitals.map((hospital, index) => (
          <HospitalCard key={index} hospital={hospital} />
        ))}
      </div>
    </div>
  );
}
