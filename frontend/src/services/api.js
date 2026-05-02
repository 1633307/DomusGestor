const API_BASE = '/api';
const TOKEN_KEY = 'domus_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Token ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const message =
      (data && (data.detail || data.non_field_errors?.[0] || JSON.stringify(data))) ||
      `Error ${res.status}`;
    throw new Error(message);
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body, opts = {}) => request(path, { method: 'POST', body, ...opts }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  patch: (path, body) => request(path, { method: 'PATCH', body }),
  del: (path) => request(path, { method: 'DELETE' }),
};

export const authApi = {
  login: (nip, password) =>
    api.post('/auth/login/', { nip, password }, { auth: false }),
  logout: () => api.post('/auth/logout/', {}),
  me: () => api.get('/auth/me/'),
};

export const propertiesApi = {
  list: (search = '') =>
    api.get(`/properties/${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  get: (id) => api.get(`/properties/${id}/`),
  create: (data) => api.post('/properties/', data),
  update: (id, data) => api.put(`/properties/${id}/`, data),
  remove: (id) => api.del(`/properties/${id}/`),
};

export const bookingsApi = {
  list: () => api.get('/bookings/reserves/'),
  get: (id) => api.get(`/bookings/reserves/${id}/`),
  create: (data) => api.post('/bookings/reserves/', data),
  // PATCH (partial update) perquè la pestanya d'edició només envia
  // alguns camps (comentaris, hostes, etc.) sense les FKs.
  update: (id, data) => api.patch(`/bookings/reserves/${id}/`, data),
  remove: (id) => api.del(`/bookings/reserves/${id}/`),
  dashboard: () => api.get('/bookings/dashboard/'),
};

