// Calculate distance between two coordinates using Haversine formula
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  
  return parseFloat(distance.toFixed(1));
};

// Get user's current location
export const getUserLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        let message = 'Unable to get location';
        if (error.code === error.PERMISSION_DENIED) {
          message = 'Location permission denied. Please enable location access in your browser.';
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          message = 'Location information is unavailable.';
        } else if (error.code === error.TIMEOUT) {
          message = 'Location request timed out.';
        }
        reject(new Error(message));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  });
};

// Update hospital distances based on user location
export const updateHospitalDistances = (hospitals, userLat, userLon) => {
  if (!hospitals || !Array.isArray(hospitals)) return hospitals;

  return hospitals.map(hospital => {
    if (hospital.coordinates && Array.isArray(hospital.coordinates)) {
      const distance = calculateDistance(
        userLat,
        userLon,
        hospital.coordinates[0],
        hospital.coordinates[1]
      );
      return {
        ...hospital,
        distance_km: distance,
        user_location: { lat: userLat, lon: userLon }
      };
    }
    return hospital;
  });
};
