const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('token');
}

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Token ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error del servidor' }));
    throw new Error(error.detail || error.non_field_errors?.[0] || JSON.stringify(error));
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  // Auth
  login: (nip, password) =>
    request('/auth/login/', { method: 'POST', body: JSON.stringify({ nip, password }) }),

  logout: () =>
    request('/auth/logout/', { method: 'POST' }),

  getMe: () =>
    request('/auth/me/'),

  register: (data) =>
    request('/auth/register/', { method: 'POST', body: JSON.stringify(data) }),

  // Properties
  getProperties: (search = '') =>
    request(`/properties/${search ? `?search=${encodeURIComponent(search)}` : ''}`),

  getProperty: (id) =>
    request(`/properties/${id}/`),

  createProperty: (data) =>
    request('/properties/', { method: 'POST', body: JSON.stringify(data) }),

  updateProperty: (id, data) =>
    request(`/properties/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteProperty: (id) =>
    request(`/properties/${id}/`, { method: 'DELETE' }),

  // Bookings
  getReserves: () =>
    request('/bookings/reserves/'),

  createReserva: (data) =>
    request('/bookings/reserves/', { method: 'POST', body: JSON.stringify(data) }),

  getInquilins: () =>
    request('/bookings/inquilins/'),

  // Dashboard
  getDashboard: () =>
    request('/bookings/dashboard/'),
};
