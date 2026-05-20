import '../styles/DoctorRecommendation.css';

export default function DoctorRecommendation({ doctors }) {
  if (!doctors || doctors.length === 0) {
    return null;
  }

  const displayedDoctors = doctors.slice(0, 2);

  return (
    <div className="doctor-section">
      <h4 className="doctors-title">Recommended Specialists</h4>
      <div className="doctors-list">
        {displayedDoctors.map((doctor, index) => (
          <div key={index} className="doctor-card">
            <div className="doctor-header">
              <p className="doctor-name">{doctor.name}</p>
              <span className="availability-badge">
                {doctor.availability}
              </span>
            </div>

            <div className="doctor-details">
              <p className="doctor-specialty">{doctor.specialty}</p>
              <p className="doctor-meta">
                {doctor.experience_years} years experience
              </p>
              <p className="doctor-floor">📍 {doctor.floor}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
