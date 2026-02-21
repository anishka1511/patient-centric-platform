import { useRef, useState } from 'react';
import SymptomForm from '../components/SymptomForm';
import LoadingScreen from '../components/LoadingScreen';
import ResultDashboard from '../components/ResultDashboard';
import { analyzeSymptoms } from '../services/api';
import { calculateDistance } from '../services/geolocation';
import '../styles/Home.css';

const COORDINATES_PATTERN = /\[?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]?/;

const toNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const normalizeUrgency = (value) => {
  const urgency = String(value || 'low').toLowerCase().trim();
  if (urgency === 'high' || urgency === 'medium' || urgency === 'low') {
    return urgency;
  }
  return 'low';
};

const mapHospitalCostLevel = (hospitalType, averageFee) => {
  const type = String(hospitalType || '').toLowerCase();
  if (type.includes('private') || type.includes('corporate')) return 'high';
  if (type.includes('public') || type.includes('government')) return 'low';

  if (averageFee == null) return 'medium';
  if (averageFee <= 500) return 'low';
  if (averageFee <= 1000) return 'medium';
  return 'high';
};

const parseOptionalLocation = (locationText) => {
  const input = String(locationText || '').trim();
  if (!input) return null;

  const match = input.match(COORDINATES_PATTERN);
  if (!match) return null;

  const latitude = toNumber(match[1]);
  const longitude = toNumber(match[2]);

  if (latitude == null || longitude == null) return null;
  return { latitude, longitude };
};

const parseLocationFromMode = (locationMode, locationValue) => {
  const input = String(locationValue || '').trim();
  if (!input) return null;

  if (locationMode === 'coordinates') {
    return parseOptionalLocation(input);
  }

  return { city: input };
};

const formatCostEstimate = (scrapingOutput) => {
  const costSummary =
    scrapingOutput?.cost_summary || scrapingOutput?.optional_nearby_doctors?.cost_summary;

  if (!costSummary) return 'Contact provider for pricing';

  const minFee = toNumber(costSummary.min_fee);
  const maxFee = toNumber(costSummary.max_fee);
  const averageFee = toNumber(costSummary.average_fee);
  const costBand = costSummary.cost_band;

  if (minFee != null && maxFee != null) {
    const base = `Rs.${Math.round(minFee)} - Rs.${Math.round(maxFee)}`;
    return costBand ? `${base} (${costBand})` : base;
  }
  if (averageFee != null) {
    return `Approx. Rs.${Math.round(averageFee)}${costBand ? ` (${costBand})` : ''}`;
  }
  return 'Contact provider for pricing';
};

const mapDoctors = (rawDoctors) => {
  if (!Array.isArray(rawDoctors)) return [];

  const seen = new Set();
  const mapped = [];

  rawDoctors.forEach((doctor) => {
    const key = [
      doctor?.name || '',
      doctor?.location || '',
      doctor?.contact_number || '',
      doctor?.consultation_fee || '',
    ].join('|');

    if (seen.has(key)) return;
    seen.add(key);

    const ratingScore = toNumber(doctor?.rating_score);
    const normalizedRating =
      ratingScore == null
        ? 80
        : Math.round(Math.max(0, Math.min(ratingScore <= 5 ? ratingScore * 20 : ratingScore, 100)));
    const fee = toNumber(doctor?.consultation_fee);

    mapped.push({
      name: doctor?.name || 'Doctor',
      specialty: doctor?.specialty || 'General Physician',
      experience_years: doctor?.experience_years ?? null,
      availability: 'Recommended',
      rating: normalizedRating,
      cost: fee == null ? 'On request' : `Rs.${Math.round(fee)}`,
      phone: doctor?.contact_number || 'Not available',
      location: doctor?.location || 'N/A',
      consultation_fee: fee,
      latitude: toNumber(doctor?.latitude),
      longitude: toNumber(doctor?.longitude),
    });
  });

  return mapped;
};

const buildHospitalsFromRecommendations = (rawHospitals, mappedDoctors, userLocation) => {
  if (!Array.isArray(rawHospitals) || rawHospitals.length === 0) return [];

  const doctorsByLocation = mappedDoctors.reduce((acc, doctor) => {
    const key = String(doctor.location || '').toLowerCase().trim();
    if (!key) return acc;
    if (!acc[key]) acc[key] = [];
    acc[key].push(doctor);
    return acc;
  }, {});

  return rawHospitals.map((hospital, index) => {
    const latitude = toNumber(hospital?.latitude);
    const longitude = toNumber(hospital?.longitude);
    const hasCoordinates = latitude != null && longitude != null;
    const locationKey = String(hospital?.location || '').toLowerCase().trim();
    const locationDoctors = doctorsByLocation[locationKey] || [];
    const fallbackDoctors = index === 0 ? mappedDoctors.slice(0, 3) : [];
    const linkedDoctors = (locationDoctors.length > 0 ? locationDoctors : fallbackDoctors).slice(0, 3);

    let distanceKm = toNumber(hospital?.distance_km);
    if (
      distanceKm == null &&
      hasCoordinates &&
      userLocation?.latitude != null &&
      userLocation?.longitude != null
    ) {
      distanceKm = calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        latitude,
        longitude
      );
    }

    const score = toNumber(hospital?.score);
    const rating =
      score == null
        ? 4.2
        : Math.max(3.5, Math.min(5, Number((3 + score * 2).toFixed(1))));

    const averageDoctorFee =
      linkedDoctors.length > 0
        ? (() => {
            const fees = linkedDoctors
              .map((doctor) => doctor.consultation_fee)
              .filter((fee) => fee != null);
            if (fees.length === 0) return null;
            return fees.reduce((sum, fee) => sum + fee, 0) / fees.length;
          })()
        : null;

    return {
      name: hospital?.hospital_name || 'Hospital',
      location: hospital?.location || 'N/A',
      distance_km: distanceKm == null ? 'N/A' : Number(distanceKm.toFixed(1)),
      rating,
      cost_level: mapHospitalCostLevel(hospital?.hospital_type, averageDoctorFee),
      insurance_supported: true,
      coordinates: hasCoordinates ? [latitude, longitude] : null,
      doctors: linkedDoctors,
      specialty: hospital?.specialties_available || '',
      hospital_type: hospital?.hospital_type || 'Unknown',
    };
  });
};

const buildHospitalsFromDoctors = (mappedDoctors, userLocation) => {
  if (!Array.isArray(mappedDoctors) || mappedDoctors.length === 0) return [];

  const groupedByLocation = mappedDoctors.reduce((acc, doctor) => {
    const key = String(doctor.location || 'Local Area').trim();
    if (!acc[key]) acc[key] = [];
    acc[key].push(doctor);
    return acc;
  }, {});

  return Object.entries(groupedByLocation).map(([location, doctors]) => {
    const firstWithCoords = doctors.find(
      (doctor) => doctor.latitude != null && doctor.longitude != null
    );

    let distanceKm = null;
    if (
      firstWithCoords &&
      userLocation?.latitude != null &&
      userLocation?.longitude != null
    ) {
      distanceKm = calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        firstWithCoords.latitude,
        firstWithCoords.longitude
      );
    }

    const rating =
      doctors.length > 0
        ? Number(
            (
              doctors.reduce((sum, doctor) => sum + (toNumber(doctor.rating) || 80), 0) /
              doctors.length /
              20
            ).toFixed(1)
          )
        : 4.0;

    const avgFee =
      doctors.length > 0
        ? (() => {
            const fees = doctors
              .map((doctor) => doctor.consultation_fee)
              .filter((fee) => fee != null);
            if (fees.length === 0) return null;
            return fees.reduce((sum, fee) => sum + fee, 0) / fees.length;
          })()
        : null;

    return {
      name: `Clinics near ${location}`,
      location,
      distance_km: distanceKm == null ? 'N/A' : Number(distanceKm.toFixed(1)),
      rating: Math.max(3.5, Math.min(5, rating)),
      cost_level: mapHospitalCostLevel('', avgFee),
      insurance_supported: true,
      coordinates:
        firstWithCoords && firstWithCoords.latitude != null && firstWithCoords.longitude != null
          ? [firstWithCoords.latitude, firstWithCoords.longitude]
          : null,
      doctors: doctors.slice(0, 3),
      specialty: doctors[0]?.specialty || '',
      hospital_type: 'Clinic Network',
    };
  });
};

const normalizeAssessmentResponse = (response) => {
  const scrapingOutput =
    response?.scraping_recommendations && typeof response.scraping_recommendations === 'object'
      ? response.scraping_recommendations
      : null;

  const primaryDoctors = Array.isArray(scrapingOutput?.recommended_doctors)
    ? scrapingOutput.recommended_doctors
    : [];
  const optionalDoctors = Array.isArray(scrapingOutput?.optional_nearby_doctors?.recommended_doctors)
    ? scrapingOutput.optional_nearby_doctors.recommended_doctors
    : [];
  const mappedDoctors = mapDoctors([...primaryDoctors, ...optionalDoctors]);

  const hospitalsFromRecommendations = buildHospitalsFromRecommendations(
    scrapingOutput?.recommended_hospitals || [],
    mappedDoctors,
    response?.user_location
  );
  const fallbackHospitals =
    hospitalsFromRecommendations.length > 0
      ? hospitalsFromRecommendations
      : buildHospitalsFromDoctors(mappedDoctors, response?.user_location);

  return {
    urgency: normalizeUrgency(response?.urgency_level),
    emergency_flag: Boolean(response?.emergency_flag),
    recommendation: response?.reasoning || 'No recommendation available.',
    specialty: response?.recommended_specialty || 'General Physician',
    care_setting: response?.care_setting || 'clinic',
    symptoms_identified: Array.isArray(response?.symptoms_identified)
      ? response.symptoms_identified
      : [],
    reasoning: response?.reasoning || '',
    safety_advice: response?.safety_advice || '',
    disclaimer: response?.disclaimer || '',
    session_id: response?.session_id || '',
    user_location: response?.user_location || null,
    scraping_input: response?.scraping_input || null,
    scraping_recommendations: scrapingOutput,
    hospitals: fallbackHospitals,
    doctors: mappedDoctors,
    cost_estimate: formatCostEstimate(scrapingOutput),
  };
};

export default function Home() {
  const sessionIdRef = useRef(
    `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [symptoms, setSymptoms] = useState(null);
  const [error, setError] = useState('');

  const handleSymptomSubmit = async ({ symptoms: userSymptoms, locationMode, locationValue }) => {
    setLoading(true);
    setError('');
    setSymptoms(userSymptoms);

    try {
      const payload = {
        message: userSymptoms,
        session_id: sessionIdRef.current,
      };

      const parsedLocation = parseLocationFromMode(locationMode, locationValue);
      if (parsedLocation) {
        payload.location = parsedLocation;
      }

      const response = await analyzeSymptoms(payload);
      setResult(normalizeAssessmentResponse(response));
    } catch (apiError) {
      const message = String(apiError?.message || 'Unable to assess symptoms right now.');
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleBackClick = () => {
    setResult(null);
    setSymptoms(null);
    setError('');
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="home">
      {result ? (
        <ResultDashboard result={result} symptoms={symptoms} onBackClick={handleBackClick} />
      ) : (
        <>
          {error && <div className="home-error">{error}</div>}
          <SymptomForm onSubmit={handleSymptomSubmit} />
        </>
      )}
    </div>
  );
}
