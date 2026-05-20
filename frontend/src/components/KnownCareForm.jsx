import { useState } from 'react';
import { getUserLocation } from '../services/geolocation';
import '../styles/SymptomForm.css';
import '../styles/KnownCareForm.css';

const KNOWN_INPUT_TYPES = [
  { value: 'diagnosis', label: 'Diagnosis' },
  { value: 'specialist', label: 'Specialist' },
  { value: 'procedure', label: 'Procedure / Surgery' },
];

export default function KnownCareForm({ onSubmit, onBack }) {
  const [inputType, setInputType] = useState('diagnosis');
  const [knownInput, setKnownInput] = useState('');
  const [details, setDetails] = useState('');
  const [locationMode, setLocationMode] = useState('region');
  const [regionName, setRegionName] = useState('');
  const [coordinateInput, setCoordinateInput] = useState('');
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState('');
  const coordinatesPattern = /^\[?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]?$/;

  const handleUseCurrentLocation = async () => {
    setLocating(true);
    setLocationError('');

    try {
      const coords = await getUserLocation();
      setCoordinateInput(`[${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}]`);
    } catch (error) {
      setLocationError(error.message);
    } finally {
      setLocating(false);
    }
  };

  const handleModeChange = (mode) => {
    setLocationMode(mode);
    setLocationError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedKnownInput = knownInput.trim();
    if (!trimmedKnownInput) return;

    const trimmedRegion = regionName.trim();
    const trimmedCoordinates = coordinateInput.trim();

    if (
      locationMode === 'coordinates' &&
      trimmedCoordinates &&
      !coordinatesPattern.test(trimmedCoordinates)
    ) {
      setLocationError('Please enter coordinates in format: [latitude, longitude]');
      return;
    }

    onSubmit({
      inputType,
      knownInput: trimmedKnownInput,
      details: details.trim(),
      locationMode,
      locationValue: locationMode === 'region' ? trimmedRegion : trimmedCoordinates,
    });
  };

  return (
    <form className="symptom-form known-care-form" onSubmit={handleSubmit}>
      {onBack && (
        <button type="button" className="form-back-button" onClick={onBack}>
          Back to Path Selection
        </button>
      )}

      <h1 className="form-title">Known Diagnosis or Specialist</h1>
      <p className="form-subtitle">
        Enter what you already know to get specialist, urgency, doctor, and hospital suggestions.
      </p>

      <div className="form-group">
        <label htmlFor="known-input-type">What are you entering?</label>
        <select
          id="known-input-type"
          className="form-input"
          value={inputType}
          onChange={(e) => setInputType(e.target.value)}
        >
          {KNOWN_INPUT_TYPES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="known-input-value">Known Diagnosis / Specialist / Procedure</label>
        <input
          id="known-input-value"
          type="text"
          className="form-input"
          placeholder="e.g., Cardiac arrest, Dentist, Brain surgery"
          value={knownInput}
          onChange={(e) => setKnownInput(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="known-input-details">Additional Notes (Optional)</label>
        <textarea
          id="known-input-details"
          className="form-input textarea"
          placeholder="Any extra context, symptoms, or concerns..."
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          rows="4"
        />
      </div>

      <div className="form-group">
        <label htmlFor="known-location">Your Location</label>
        <div className="location-mode-buttons" role="group" aria-label="Location input mode">
          <button
            type="button"
            className={`mode-button ${locationMode === 'region' ? 'active' : ''}`}
            onClick={() => handleModeChange('region')}
          >
            Region Name
          </button>
          <button
            type="button"
            className={`mode-button ${locationMode === 'coordinates' ? 'active' : ''}`}
            onClick={() => handleModeChange('coordinates')}
          >
            Coordinates
          </button>
        </div>

        <div className="location-input-wrapper">
          <input
            id="known-location"
            type="text"
            className="form-input"
            placeholder={
              locationMode === 'region'
                ? 'Enter area name (e.g., Kothrud, Shivajinagar)'
                : 'Enter coordinates [latitude, longitude]'
            }
            value={locationMode === 'region' ? regionName : coordinateInput}
            onChange={(e) =>
              locationMode === 'region'
                ? setRegionName(e.target.value)
                : setCoordinateInput(e.target.value)
            }
          />
          {locationMode === 'coordinates' && (
            <button
              type="button"
              className={`location-button ${locating ? 'loading' : ''}`}
              onClick={handleUseCurrentLocation}
              disabled={locating}
              title="Use your current location"
            >
              {locating ? 'Detecting...' : 'Use Current Location'}
            </button>
          )}
        </div>
        {locationError && <div className="location-error">{locationError}</div>}
      </div>

      <button type="submit" className="submit-button known-submit-button">
        Find Doctors & Hospitals
      </button>
    </form>
  );
}
