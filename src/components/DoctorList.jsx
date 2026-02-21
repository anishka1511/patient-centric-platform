import '../styles/DoctorList.css';

// Helper function to normalize rating to 0-5 numeric scale
function formatDoctorRating(ratingValue) {
  if (ratingValue == null || ratingValue === '') return 'N/A';

  const numeric =
    typeof ratingValue === 'string'
      ? Number(ratingValue.replace('%', '').trim())
      : Number(ratingValue);

  if (!Number.isFinite(numeric)) return 'N/A';

  const ratingOnFive = numeric > 5 ? numeric / 20 : numeric;
  const clampedRating = Math.max(0, Math.min(5, ratingOnFive));
  return clampedRating.toFixed(1);
}

// Helper function to format phone number
function formatPhoneNumber(phone) {
  if (!phone) return 'N/A';
  
  // Remove .0 at the end if present
  const cleanPhone = phone.toString().replace('.0', '');
  
  // Format Indian phone number: +91 XXXXX XXXXX
  if (cleanPhone.length >= 10) {
    const lastTen = cleanPhone.slice(-10);
    return `+91 ${lastTen.slice(0, 5)} ${lastTen.slice(5)}`;
  }
  
  return cleanPhone;
}

// Helper function to parse cost
function parseCost(costStr) {
  if (!costStr) return 'On Request';
  
  // Handle different formats and decode Unicode
  let cost = String(costStr).replace(/[\u200B-\u200D\uFEFF]/g, ''); // Remove zero-width chars
  
  // Try to extract just the rupee amount
  if (cost.includes('₹')) {
    return cost;
  }
  
  // If it's just numbers, format as rupees
  const numMatch = cost.match(/\d+/);
  if (numMatch) {
    return `₹${numMatch[0]}`;
  }
  
  return cost;
}

export default function DoctorList({ hospitals = [], doctors = [], specialty }) {
  // Extract all doctors from all hospitals
  const doctorsFromHospitals = [];
  hospitals.forEach((hospital) => {
    if (hospital.doctors && Array.isArray(hospital.doctors)) {
      hospital.doctors.forEach((doctor) => {
        doctorsFromHospitals.push({
          ...doctor,
          hospital_name: hospital.name,
          hospital_distance: hospital.distance_km,
          hospital_rating: hospital.rating,
          hospital_cost: hospital.cost_level,
          hospital_insurance: hospital.insurance_supported
        });
      });
    }
  });

  const sourceDoctors = doctors.length > 0 ? doctors : doctorsFromHospitals;
  const seenDoctors = new Set();
  const allDoctors = sourceDoctors
    .filter((doctor) => {
      const key = [
        doctor?.name || '',
        doctor?.specialty || '',
        doctor?.location || '',
        doctor?.phone || doctor?.contact_number || ''
      ].join('|');
      if (seenDoctors.has(key)) return false;
      seenDoctors.add(key);
      return true;
    });

  if (allDoctors.length === 0) {
    return (
      <div className="doctor-list-container">
        <div className="empty-state">
          <p>No doctors available for {specialty}.</p>
        </div>
      </div>
    );
  }

  // Sort by availability (Available Today first)
  const sortedDoctors = [...allDoctors].sort((a, b) => {
    const aAvailable = a.availability?.includes('Available Today') ? 0 : 1;
    const bAvailable = b.availability?.includes('Available Today') ? 0 : 1;
    return aAvailable - bAvailable;
  });

  return (
    <div className="doctor-list-container">
      <div className="doctors-header">
        <h2 className="doctors-main-title">👨‍⚕️ Available Doctors</h2>
        <p className="doctors-subtitle">{allDoctors.length} specialists found</p>
      </div>

      <div className="doctors-grid">
        {sortedDoctors.map((doctor, index) => (
          <div key={index} className="doctor-list-card">
            <div className="doctor-card-header">
              <div className="doctor-info-top">
                <h3 className="doctor-list-name">{doctor.name}</h3>
                <span className={`availability-badge ${doctor.availability?.includes('Available Today') ? 'available' : 'scheduled'}`}>
                  {doctor.availability || 'Contact for availability'}
                </span>
              </div>
              <p className="doctor-list-specialty">👨‍⚕️ {doctor.specialty}</p>
            </div>

            <div className="doctor-card-body">
              <div className="doctor-stats">
                <div className="stat-item">
                  <span className="stat-label">Experience</span>
                  <span className="stat-value">
                    {doctor.experience_years != null ? `${doctor.experience_years} yrs` : 'N/A'}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Rating</span>
                  <span className="stat-value">
                    {formatDoctorRating(doctor.rating)}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Per Visit</span>
                  <span className="stat-value">{parseCost(doctor.cost)}</span>
                </div>
              </div>

              {doctor.hospital_name && (
                <div className="hospital-info-section">
                  <p className="hospital-info-label">🏥 Hospital</p>
                  <p className="hospital-info-name">{doctor.hospital_name}</p>
                  <div className="hospital-metrics">
                    <span className="metric">
                      📍 {doctor.hospital_distance ?? 'N/A'} {Number.isFinite(Number(doctor.hospital_distance)) ? 'km away' : ''}
                    </span>
                    <span className="metric">Hospital Rating: {doctor.hospital_rating ?? 'N/A'}/5</span>
                    {doctor.hospital_cost && (
                      <span className={`metric cost-${doctor.hospital_cost}`}>
                        {doctor.hospital_cost.charAt(0).toUpperCase() + doctor.hospital_cost.slice(1)}
                      </span>
                    )}
                  </div>
                  {doctor.hospital_insurance && (
                    <span className="insurance-tag">✓ Insurance Accepted</span>
                  )}
                </div>
              )}

              {doctor.location && (
                <div className="location-info">
                  <span className="location-label">🏢 Floor/Location</span>
                  <span className="location-value">{doctor.location}</span>
                </div>
              )}

              {doctor.phone && doctor.phone !== 'Not available' && (
                <div className="contact-info">
                  <span className="contact-label">📞 Call Doctor</span>
                  <span className="contact-value">{formatPhoneNumber(doctor.phone)}</span>
                </div>
              )}
            </div>

            <div className="doctor-card-footer">
              <button className="book-button">Book Appointment</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
