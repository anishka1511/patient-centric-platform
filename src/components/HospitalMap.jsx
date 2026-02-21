import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/HospitalMap.css';

// Pune service areas with coordinates
const PUNE_SERVICE_AREAS = {
  'baner': [18.5590, 73.7890],
  'baner road': [18.5594, 73.7876],
  'aundh': [18.5604, 73.8071],
  'balewadi': [18.5689, 73.7720],
  'pashan': [18.5354, 73.7850],
  'wakad': [18.5998, 73.7616],
  'hinjewadi': [18.5913, 73.7389],
  'pimpri-chinchwad': [18.6298, 73.7997],
  'kothrud': [18.5074, 73.8077],
  'karve nagar': [18.5024, 73.8166],
  'paud road': [18.5095, 73.7986],
  'warje': [18.4865, 73.8010],
  'shivajinagar': [18.5308, 73.8475],
  'kharadi': [18.5511, 73.9422],
  'viman nagar': [18.5679, 73.9154],
  'hadapsar': [18.5089, 73.9260],
  'wagholi': [18.5793, 73.9790],
  'magarpatta': [18.5167, 73.9346],
  'koregaon park': [18.5362, 73.8940],
  'fc road': [18.5196, 73.8409],
  'nibm': [18.4590, 73.8966],
  'swargate': [18.5018, 73.8636],
};

// Component to handle map bounds fitting
function MapBounds({ hospitals, areas }) {
  const map = useMap();

  useEffect(() => {
    const allCoords = [
      ...hospitals
        .filter(h => h.coordinates && Array.isArray(h.coordinates))
        .map(h => h.coordinates),
      ...Object.values(areas),
    ];

    if (allCoords.length > 0) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [hospitals, areas, map]);

  return null;
}

// Service area marker component with red pin icon
function ServiceAreaMarker({ areaName, coordinates }) {
  // Create red pin icon SVG
  const redPinIcon = new L.Icon({
    iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI1MCIgdmlld0JveD0iMCAwIDQwIDUwIj48ZGVmcz48ZmlsdGVyIGlkPSJzaGFkb3ciIHg9Ii01MCUiIHk9Ii01MCUiIHdpZHRoPSIyMDAlIiBoZWlnaHQ9IjIwMCUiPjxmZU9mZnNldCBpbj0iU291cmNlR3JhcGhpYyIgZHg9IjAiIGR5PSIyIi8+PGZlR2F1c3NpYW5CbHVyIGluPSJvZmZzZXQiIHN0ZERldmlhdGlvbj0iMyIvPjxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjwvZmVNZXJnZT48L2ZpbHRlcj48L2RlZnM+PHBhdGggZmlsdGVyPSJ1cmwoI3NoYWRvdykiIGQ9Ik0yMCAwQzguOTU0IDAgMCA4Ljk1NCAwIDIwYzAgMTAgMjAgMzAgMjAgMzBzMjAtMjAgMjAtMzBDNDAgOC45NTQgMzEuMDQ2IDAgMjAgMHptMCAyOWMtNS4wMDggMC05LTMuOTkyLTktOXMzLjk5Mi05IDktOSA5IDMuOTkyIDkgOS0zLjk5MiA5LTkgOXoiIGZpbGw9IiNlZjQ0NDQiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==',
    iconSize: [40, 50],
    iconAnchor: [20, 50],
    popupAnchor: [0, -50],
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    shadowSize: [41, 41],
    shadowAnchor: [12, 41],
  });

  return (
    <Marker position={coordinates} icon={redPinIcon}>
      <Popup maxWidth={250}>
        <div className="area-popup">
          <div className="area-name">📍 {areaName.toUpperCase()}</div>
          <div className="area-coords">
            {coordinates[0].toFixed(4)}, {coordinates[1].toFixed(4)}
          </div>
          <div className="area-coverage">Service Area Available</div>
        </div>
      </Popup>
    </Marker>
  );
}

// User location marker component
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
          <br/>
          {coordinates[0].toFixed(4)}, {coordinates[1].toFixed(4)}
        </div>
      </Popup>
    </Marker>
  );
}

// Hospital marker component
function HospitalMarker({ hospital, index }) {
  const colors = [
    '#14B8A6', // Teal
    '#0891B2', // Cyan
    '#06B6D4', // Sky
    '#0EA5E9', // Blue
    '#3B82F6', // Purple
  ];

  const color = colors[index % colors.length];

  return (
    <CircleMarker
      center={hospital.coordinates}
      radius={18}
      fill={true}
      fillColor={color}
      fillOpacity={0.95}
      stroke={true}
      color="white"
      weight={3}
      opacity={1}
    >
      <Popup maxWidth={280}>
        <div className="hospital-popup">
          <div className="popup-header">
            <h4 className="popup-name">{hospital.name}</h4>
            <div className="popup-rating">⭐ {hospital.rating}/5</div>
          </div>

          <div className="popup-content">
            <div className="popup-row">
              <span className="popup-label">📍 Distance:</span>
              <span className="popup-value">{hospital.distance_km} km</span>
            </div>

            <div className="popup-row">
              <span className="popup-label">💰 Cost:</span>
              <span className="popup-value popup-cost-{hospital.cost_level}">
                {hospital.cost_level.charAt(0).toUpperCase() +
                  hospital.cost_level.slice(1)}
              </span>
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
    </CircleMarker>
  );
}

export default function HospitalMap({ hospitals, user_location }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredHospitals, setFilteredHospitals] = useState(hospitals);
  const [showAreas, setShowAreas] = useState(true);
  
  // Use user location if available, otherwise default to Pune center
  const puneCenter = user_location 
    ? [user_location.latitude, user_location.longitude]
    : [18.5204, 73.8567];

  useEffect(() => {
    const filtered = hospitals.filter(hospital =>
      hospital.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hospital.specialty?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredHospitals(filtered);
  }, [searchTerm, hospitals]);

  const validHospitals = filteredHospitals.filter(
    h => h.coordinates && Array.isArray(h.coordinates)
  );

  return (
    <div className="hospital-map-container">
      <div className="map-header">
        <h3 className="map-title">🗺️ Hospital Network Map</h3>
        <p className="map-subtitle">
          {validHospitals.length} hospitals | {Object.keys(PUNE_SERVICE_AREAS).length} service areas
        </p>
      </div>

      <div className="map-controls">
        <div className="map-search">
          <input
            type="text"
            placeholder="🔍 Search hospitals or specialties..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <label className="toggle-areas">
          <input
            type="checkbox"
            checked={showAreas}
            onChange={(e) => setShowAreas(e.target.checked)}
          />
          <span>Show Service Areas</span>
        </label>
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-dot legend-hospital"></div>
          <span>Hospitals</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot legend-area"></div>
          <span>Service Areas</span>
        </div>
      </div>

      {validHospitals.length > 0 || showAreas ? (
        <MapContainer
          center={puneCenter}
          zoom={12}
          scrollWheelZoom={true}
          className="hospital-map"
          style={{ borderRadius: '12px' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapBounds hospitals={validHospitals} areas={Object.values(PUNE_SERVICE_AREAS)} />

          {/* Service areas layer (rendered first, behind hospitals) */}
          {showAreas &&
            Object.entries(PUNE_SERVICE_AREAS).map(([areaName, coordinates], idx) => (
              <ServiceAreaMarker
                key={`area-${idx}`}
                areaName={areaName}
                coordinates={coordinates}
              />
            ))}

          {/* User location marker */}
          {user_location && (
            <UserLocationMarker coordinates={[user_location.latitude, user_location.longitude]} />
          )}

          {/* Hospitals layer (rendered on top) */}
          {validHospitals.map((hospital, index) => (
            <HospitalMarker key={`hosp-${index}`} hospital={hospital} index={index} />
          ))}
        </MapContainer>
      ) : (
        <div className="map-empty">
          <p>📍 No hospitals found matching your search</p>
        </div>
      )}

      <div className="map-info">
        <p className="info-text">
          💡 <strong>Tip:</strong> Colored hospital pins show our medical partners. Red pins mark all service areas in Pune. Click any pin for details.
        </p>
      </div>
    </div>
  );
}
