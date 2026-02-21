import { useState } from 'react';
import SymptomForm from '../components/SymptomForm';
import LoadingScreen from '../components/LoadingScreen';
import ResultDashboard from '../components/ResultDashboard';
import { updateHospitalDistances } from '../services/geolocation';
// Import all specialty data
import cardiologistData from '../mock/cardiologist.json';
import dentistData from '../mock/dentist.json';
import generalPhysicianData from '../mock/generalphysician.json';
import orthopedicData from '../mock/orthopedic.json';
import gynacData from '../mock/gynac.json';
import obstetricianData from '../mock/obsstetrician.json';
import pediatricianData from '../mock/pediatrician.json';
import dermatologistData from '../mock/dermatologist.json';
import ophthalmologistData from '../mock/ophthalmologist.json';
import internalMedicineData from '../mock/internalmedicine.json';
import psychiatristData from '../mock/psychiatrist.json';
import urologistData from '../mock/urologist.json';
import entData from '../mock/entspecialist.json';
import oncologistData from '../mock/oncologist.json';
import endocrinologistData from '../mock/endocrinologist.json';
import gastroenterologistData from '../mock/gastroenterologist.json';
import nephrologistData from '../mock/nephrologist.json';
import pulmonologistData from '../mock/pulmonologist.json';
import '../styles/Home.css';

// Map specialty keys to imported data
const SPECIALTY_DATA = {
  'Cardiologist': cardiologistData,
  'Dentist': dentistData,
  'General Physician': generalPhysicianData,
  'Orthopedic': orthopedicData,
  'Gynac': gynacData,
  'Obsstetrician': obstetricianData,
  'Pediatrician': pediatricianData,
  'Dermatologist': dermatologistData,
  'Ophthalmologist': ophthalmologistData,
  'Internal Medicine': internalMedicineData,
  'Psychiatrist': psychiatristData,
  'Urologist': urologistData,
  'Ent Specialist': entData,
  'Oncologist': oncologistData,
  'Endocrinologist': endocrinologistData,
  'Gastroenterologist': gastroenterologistData,
  'Nephrologist': nephrologistData,
  'Pulmonologist': pulmonologistData
};

// Symptom to specialty mapping for auto-detection
const SYMPTOM_SPECIALTY_MAP = {
  chest: 'Cardiologist',
  heart: 'Cardiologist',
  cardiac: 'Cardiologist',
  breath: 'Cardiologist',
  palpitation: 'Cardiologist',
  arrhythmia: 'Cardiologist',
  tooth: 'Dentist',
  teeth: 'Dentist',
  cavity: 'Dentist',
  gum: 'Dentist',
  decay: 'Dentist',
  joint: 'Orthopedic',
  bone: 'Orthopedic',
  fracture: 'Orthopedic',
  spine: 'Orthopedic',
  muscle: 'Orthopedic',
  pregnancy: 'Obsstetrician',
  pregnant: 'Obsstetrician',
  labor: 'Obsstetrician',
  delivery: 'Obsstetrician',
  period: 'Gynac',
  menstrual: 'Gynac',
  gynec: 'Gynac',
  skin: 'Dermatologist',
  rash: 'Dermatologist',
  acne: 'Dermatologist',
  eczema: 'Dermatologist',
  psoriasis: 'Dermatologist',
  eye: 'Ophthalmologist',
  vision: 'Ophthalmologist',
  sight: 'Ophthalmologist',
  glasses: 'Ophthalmologist',
  contact: 'Ophthalmologist',
  ear: 'Ent Specialist',
  nose: 'Ent Specialist',
  throat: 'Ent Specialist',
  cold: 'General Physician',
  cough: 'General Physician',
  fever: 'General Physician',
  flu: 'General Physician',
  nausea: 'General Physician',
  headache: 'General Physician',
  kidney: 'Nephrologist',
  renal: 'Nephrologist',
  lung: 'Pulmonologist',
  respiratory: 'Pulmonologist',
  breathing: 'Pulmonologist',
  cancer: 'Oncologist',
  tumor: 'Oncologist',
  diabetes: 'Endocrinologist',
  hormone: 'Endocrinologist',
  thyroid: 'Endocrinologist',
  stomach: 'Gastroenterologist',
  digestive: 'Gastroenterologist',
  constipation: 'Gastroenterologist',
  diarrhea: 'Gastroenterologist',
  acid: 'Gastroenterologist',
  urine: 'Urologist',
  bladder: 'Urologist',
  prostate: 'Urologist',
  child: 'Pediatrician',
  baby: 'Pediatrician',
  infant: 'Pediatrician',
  mental: 'Psychiatrist',
  depression: 'Psychiatrist',
  anxiety: 'Psychiatrist',
  stress: 'Psychiatrist'
};

// Helper function to auto-detect specialty from symptoms
const autoDetectSpecialty = (symptoms) => {
  const lowerSymptoms = symptoms.toLowerCase();
  
  for (const [keyword, specialty] of Object.entries(SYMPTOM_SPECIALTY_MAP)) {
    if (lowerSymptoms.includes(keyword)) {
      return specialty;
    }
  }
  
  // Default to General Physician if no match
  return 'General Physician';
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [symptoms, setSymptoms] = useState(null);

  const handleSymptomSubmit = async ({ symptoms, location }) => {
    setLoading(true);
    setSymptoms(symptoms);

    // Simulate API call with timeout
    setTimeout(() => {
      // Auto-detect specialty from symptoms
      const selectedSpecialty = autoDetectSpecialty(symptoms);

      // Get the appropriate data for selected specialty
      let selectedData = { ...SPECIALTY_DATA[selectedSpecialty] || SPECIALTY_DATA['General Physician'] };

      // Extract coordinates from location string if available (format: [lat, lon])
      const coordMatch = location.match(/\[([-\d.]+),\s*([-\d.]+)\]/);
      if (coordMatch && coordMatch[1] && coordMatch[2]) {
        const userLat = parseFloat(coordMatch[1]);
        const userLon = parseFloat(coordMatch[2]);
        
        // Update hospital distances based on user location
        if (selectedData.hospitals && Array.isArray(selectedData.hospitals)) {
          selectedData = {
            ...selectedData,
            hospitals: updateHospitalDistances(selectedData.hospitals, userLat, userLon),
            user_location: { latitude: userLat, longitude: userLon }
          };
        }
      }

      setResult(selectedData);
      setLoading(false);
    }, 1500);
  };

  const handleBackClick = () => {
    setResult(null);
    setSymptoms(null);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (result) {
    return <ResultDashboard result={result} symptoms={symptoms} onBackClick={handleBackClick} />;
  }

  return <SymptomForm onSubmit={handleSymptomSubmit} />;
}
