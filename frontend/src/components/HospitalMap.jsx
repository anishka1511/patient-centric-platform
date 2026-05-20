import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Popup, useMap, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/HospitalMap.css';

const toFiniteNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

function MapBounds({ hospitals, userCoordinates, searchTerm }) {
  const map = useMap();

  useEffect(() => {
    const hospitalCoords = hospitals
      .filter((h) => h.coordinates && Array.isArray(h.coordinates))
      .map((h) => h.coordinates);

    if (hospitalCoords.length === 0) {
      if (userCoordinates && Array.isArray(userCoordinates)) {
        map.setView(userCoordinates, 12);
      }
      return;
    }

    const hasSearch = String(searchTerm || '').trim().length > 0;

    if (hasSearch) {
      if (hospitalCoords.length === 1) {
        map.setView(hospitalCoords[0], 16);
        return;
      }

      const searchBounds = L.latLngBounds(hospitalCoords);
      map.fitBounds(searchBounds, { padding: [40, 40], maxZoom: 15 });
      return;
    }

    const allCoords = [...hospitalCoords];
    if (userCoordinates && Array.isArray(userCoordinates)) {
      allCoords.push(userCoordinates);
    }

    if (allCoords.length > 0) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [hospitals, userCoordinates, searchTerm, map]);

  return null;
}

function buildHospitalIcon(color) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="30" viewBox="0 0 22 30">
      <path d="M11 1C5.5 1 1 5.5 1 11c0 5.8 10 18 10 18s10-12.2 10-18C21 5.5 16.5 1 11 1z"
            fill="${color}" stroke="white" stroke-width="2"/>
      <circle cx="11" cy="11" r="3.8" fill="white"/>
    </svg>`;

  const redPinIcon = new L.Icon({
    iconUrl: `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`,
    iconSize: [22, 30],
    iconAnchor: [11, 30],
    popupAnchor: [0, -30],
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    shadowSize: [28, 28],
    shadowAnchor: [8, 28],
  });

  return redPinIcon;
}

function UserLocationMarker({ coordinates }) {
  const userIcon = new L.Icon({
    iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDQwIDQwIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxOCIgZmlsbD0iIzMzODhkZiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iOCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  });

  return (
    <Marker position={coordinates} icon={userIcon}>
      <Popup maxWidth={200}>
        <div style={{ textAlign: 'center', color: '#333' }}>
          <strong>📍 Your Location</strong>
          <br />
          {coordinates[0].toFixed(4)}, {coordinates[1].toFixed(4)}
        </div>
      </Popup>
    </Marker>
  );
}

function HospitalMarker({ hospital, index }) {
  const colors = ['#14B8A6', '#0891B2', '#06B6D4', '#0EA5E9', '#3B82F6'];
  const color = colors[index % colors.length];
  const hospitalIcon = buildHospitalIcon(color);
  const costLevel = hospital.cost_level || 'medium';
  const costLabel = costLevel.charAt(0).toUpperCase() + costLevel.slice(1);
  const distanceLabel =
    hospital.distance_km == null || hospital.distance_km === 'N/A'
      ? 'N/A'
      : `${hospital.distance_km} km`;
  const ratingLabel = hospital.rating != null ? hospital.rating : 'N/A';

  return (
    <Marker position={hospital.coordinates} icon={hospitalIcon}>
      <Popup maxWidth={280}>
        <div className="hospital-popup">
          <div className="popup-header">
            <h4 className="popup-name">{hospital.name}</h4>
            <div className="popup-rating">Rating: {ratingLabel}/5</div>
          </div>

          <div className="popup-content">
            <div className="popup-row">
              <span className="popup-label">📍 Distance:</span>
              <span className="popup-value">{distanceLabel}</span>
            </div>

            <div className="popup-row">
              <span className="popup-label">📌 Location:</span>
              <span className="popup-value">{hospital.location || 'N/A'}</span>
            </div>

            <div className="popup-row">
              <span className="popup-label">💰 Cost:</span>
              <span className={`popup-value popup-cost-${costLevel}`}>{costLabel}</span>
            </div>

            <div className="popup-row">
              <span className="popup-label">🏥 Insurance:</span>
              <span className="popup-value">
                {hospital.insurance_supported ? '✅ Supported' : '❌ Not Supported'}
              </span>
            </div>

            {hospital.doctors && hospital.doctors.length > 0 && (
              <div className="popup-doctors">
                <div className="popup-label">👨‍⚕️ Available Doctors:</div>
                {hospital.doctors.slice(0, 2).map((doc, idx) => (
                  <div key={idx} className="doctor-item">
                    <div className="doctor-name">{doc.name}</div>
                    <div className="doctor-specialty">{doc.specialty}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="popup-footer">
            <button className="popup-btn">View Details</button>
          </div>
        </div>
      </Popup>
    </Marker>
  );
}

export default function HospitalMap({ hospitals = [], user_location }) {
  const [searchTerm, setSearchTerm] = useState('');
  const normalizedHospitals = useMemo(() => {
    const seen = new Set();
    const mapped = [];

    hospitals.forEach((hospital, index) => {
      const latitude = toFiniteNumber(hospital?.coordinates?.[0]);
      const longitude = toFiniteNumber(hospital?.coordinates?.[1]);
      if (latitude == null || longitude == null) return;

      const id =
        String(hospital?.id || '').trim() ||
        `${String(hospital?.name || 'hospital').toLowerCase()}|${String(hospital?.location || '').toLowerCase()}|${latitude}|${longitude}`;
      if (seen.has(id)) return;
      seen.add(id);

      mapped.push({
        ...hospital,
        id,
        coordinates: [latitude, longitude],
        _markerIndex: index,
      });
    });

    return mapped;
  }, [hospitals]);

  const filteredHospitals = useMemo(() => {
    const term = searchTerm.toLowerCase().trim();
    if (!term) return normalizedHospitals;

    return normalizedHospitals.filter((hospital) =>
      hospital.name.toLowerCase().includes(term) ||
      String(hospital.location || '').toLowerCase().includes(term)
    );
  }, [normalizedHospitals, searchTerm]);

  const locationCount = useMemo(
    () =>
      new Set(
        normalizedHospitals
          .map((hospital) => String(hospital.location || '').toLowerCase().trim())
          .filter(Boolean)
      ).size,
    [normalizedHospitals]
  );

  const userLatitude = toFiniteNumber(user_location?.latitude);
  const userLongitude = toFiniteNumber(user_location?.longitude);
  const hasUserCoordinates =
    userLatitude != null &&
    userLongitude != null;

  const puneCenter = hasUserCoordinates
    ? [userLatitude, userLongitude]
    : [18.5204, 73.8567];

  const validHospitals = filteredHospitals.filter(
    (hospital) =>
      hospital.coordinates &&
      Array.isArray(hospital.coordinates) &&
      toFiniteNumber(hospital.coordinates[0]) != null &&
      toFiniteNumber(hospital.coordinates[1]) != null
  );
  const hasRenderableMapData = validHospitals.length > 0 || hasUserCoordinates;

  return (
    <div className="hospital-map-container">
      <div className="map-header">
        <h3 className="map-title">🗺️ Hospital Network Map</h3>
        <p className="map-subtitle">
          {validHospitals.length} hospitals shown | {locationCount} locations
        </p>
      </div>

      <div className="map-controls">
        <div className="map-search">
          <input
            type="text"
            placeholder="🔍 Search hospitals or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-dot legend-hospital"></div>
          <span>Hospitals</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot legend-user"></div>
          <span>Your Location</span>
        </div>
      </div>

      {hasRenderableMapData ? (
        <MapContainer
          center={puneCenter}
          zoom={12}
          scrollWheelZoom
          className="hospital-map"
          style={{ borderRadius: '12px' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapBounds
            hospitals={validHospitals}
            userCoordinates={hasUserCoordinates ? [userLatitude, userLongitude] : null}
            searchTerm={searchTerm}
          />

          {hasUserCoordinates && (
            <UserLocationMarker coordinates={[userLatitude, userLongitude]} />
          )}

          {validHospitals.map((hospital, index) => (
            <HospitalMarker
              key={hospital.id || `hosp-${hospital._markerIndex ?? index}`}
              hospital={hospital}
              index={hospital._markerIndex ?? index}
            />
          ))}
        </MapContainer>
      ) : (
        <div className="map-empty">
          <p>📍 No hospitals found matching your search</p>
        </div>
      )}

      <div className="map-info">
        <p className="info-text">
          💡 <strong>Tip:</strong> Only hospital pins and your location pin are shown. Click a hospital pin for details.
        </p>
      </div>
    </div>
  );
}
