// Utility function to match doctors to hospitals by location
export const matchDoctorsToHospitals = (doctors, hospitalData, specialty) => {
  if (!doctors || !Array.isArray(doctors)) return hospitalData;

  // Extract unique locations from doctors
  const doctorsByLocation = {};
  doctors.forEach(doctor => {
    if (doctor.doctors_location) {
      const location = doctor.doctors_location.trim().replace(/,\s*$/, '').toLowerCase();
      if (!doctorsByLocation[location]) {
        doctorsByLocation[location] = [];
      }
      doctorsByLocation[location].push(doctor);
    }
  });

  // Update hospital data with doctors from CSV
  const updatedHospitals = hospitalData.hospitals.map(hospital => {
    // Extract hospital location from name (e.g., "Apollo Hospitals, Baner" → "Baner")
    const hospitalLocation = hospital.name.split(',').pop().trim().toLowerCase();

    // Find matching doctors from CSV by location
    let matchedDoctors = doctorsByLocation[hospitalLocation] || [];

    // If no exact match, try partial matching
    if (matchedDoctors.length === 0) {
      Object.keys(doctorsByLocation).forEach(location => {
        if (hospitalLocation.includes(location) || location.includes(hospitalLocation)) {
          matchedDoctors = doctorsByLocation[location];
        }
      });
    }

    // Filter doctors by specialty and limit to 3 per hospital
    const specialtyFilter = specialty.toLowerCase();
    const filteredDoctors = matchedDoctors
      .filter(doc => doc.specialty && doc.specialty.toLowerCase().includes(specialtyFilter))
      .slice(0, 3)
      .map(doc => ({
        name: doc.doctors_name || 'Dr. Unknown',
        specialty: doc.specialty || specialty,
        experience_years: parseInt(doc.doctors_profession?.match(/\d+/) || '10') || 10,
        floor: 'Department of ' + (doc.specialty || specialty),
        availability: doc.doctors_rating ? 'Available Today' : 'Schedule Appointment',
        rating: doc.doctors_rating || '90%',
        cost: doc.doctors_cost || '₹500',
        phone: doc.doctors_number || 'Not listed'
      }));

    // Return hospital with updated doctors (keep existing if no matches)
    if (filteredDoctors.length > 0) {
      return {
        ...hospital,
        doctors: filteredDoctors
      };
    }

    return hospital;
  });

  return {
    ...hospitalData,
    hospitals: updatedHospitals
  };
};

// Parse CSV text and return array of doctor objects
export const parseCSVData = (csvText) => {
  const lines = csvText.split(/\r?\n/);
  const headers = (lines[0] || '')
    .replace(/^\uFEFF/, '')
    .split(',')
    .map(h => h.trim());
  const doctors = [];

  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;

    // Simple CSV parsing (handles quoted fields with commas)
    const values = [];
    let currentValue = '';
    let insideQuotes = false;

    for (let j = 0; j < lines[i].length; j++) {
      const char = lines[i][j];
      const nextChar = lines[i][j + 1];

      if (char === '"') {
        insideQuotes = !insideQuotes;
      } else if (char === ',' && !insideQuotes) {
        values.push(currentValue.trim().replace(/^"|"$/g, ''));
        currentValue = '';
      } else {
        currentValue += char;
      }
    }
    values.push(currentValue.trim().replace(/^"|"$/g, ''));

    const doctor = {};
    headers.forEach((header, index) => {
      doctor[header] = values[index] || '';
    });

    if (doctor.doctors_name) {
      doctors.push(doctor);
    }
  }

  return doctors;
};

// Get summary statistics from imported doctor data
export const getDoctorStats = (doctors) => {
  if (!Array.isArray(doctors)) return {};

  const specialties = {};
  const locations = {};

  doctors.forEach(doctor => {
    if (doctor.specialty) {
      specialties[doctor.specialty] = (specialties[doctor.specialty] || 0) + 1;
    }
    if (doctor.doctors_location) {
      const location = doctor.doctors_location.trim().replace(/,\s*$/, '');
      locations[location] = (locations[location] || 0) + 1;
    }
  });

  return {
    totalDoctors: doctors.length,
    specialties,
    locations,
    uniqueSpecialties: Object.keys(specialties).length,
    uniqueLocations: Object.keys(locations).length
  };
};
