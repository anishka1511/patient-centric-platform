const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`
).replace(/\/+$/, '');

const postJson = async (path, payload) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API request failed with status ${response.status}`);
  }

  return response.json();
};

export const analyzeSymptoms = async (payload) => {
  try {
    return await postJson('/api/assess', payload);
  } catch (error) {
    if (!String(error?.message || '').includes('404')) {
      throw error;
    }
    return postJson('/api/analyze', payload);
  }
};
