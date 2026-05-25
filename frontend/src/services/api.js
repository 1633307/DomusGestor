const API_BASE = "/api";
const TOKEN_KEY = "domus_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Token ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    if (!res.ok) throw new Error(`Error ${res.status}: resposta inesperada del servidor.`);
  }

  if (!res.ok) {
    const genericMessage =
      (data && (data.detail || data.non_field_errors?.[0])) ||
      `Error ${res.status}`;
    const err = new Error(genericMessage);
    if (data && typeof data === 'object' && !data.detail && !data.non_field_errors) {
      err.fieldErrors = data;
    }
    throw err;
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body, opts = {}) =>
    request(path, { method: "POST", body, ...opts }),
  put: (path, body) => request(path, { method: "PUT", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  del: (path) => request(path, { method: "DELETE" }),
};

export const authApi = {
  login: (nip, password) =>
    api.post("/auth/login/", { nip, password }, { auth: false }),
  logout: () => api.post("/auth/logout/", {}),
  me: () => api.get("/auth/me/"),
};

export const propertiesApi = {
  list: (search = "") =>
    api.get(
      `/properties/${search ? `?search=${encodeURIComponent(search)}` : ""}`,
    ),
  get: (id) => api.get(`/properties/${id}/`),
  create: (data) => api.post("/properties/", data),
  update: (id, data) => api.put(`/properties/${id}/`, data),
  patch: (id, data) => api.patch(`/properties/${id}/`, data),
  remove: (id) => api.del(`/properties/${id}/`),
};

export const immobiliariaApi = {
  list: () => api.get('/auth/info-immobiliaria/'),
  create: (data) => api.post('/auth/info-immobiliaria/', data),
  update: (id, data) => api.put(`/auth/info-immobiliaria/${id}/`, data),
};

export const bookingsApi = {
  list: () => api.get("/bookings/reserves/"),
  listByImmoble: (immobleId) => api.get(`/bookings/reserves/?immoble=${immobleId}`),
  get: (id) => api.get(`/bookings/reserves/${id}/`),
  preview: (data) => api.post("/bookings/reserves/preview/", data),
  create: (data) => api.post("/bookings/reserves/", data),
  // PATCH (partial update) perquè la pestanya d'edició només envia
  // alguns camps (comentaris, hostes, etc.) sense les FKs.
  update: (id, data) => api.patch(`/bookings/reserves/${id}/`, data),
  remove: (id) => api.del(`/bookings/reserves/${id}/`),
  dashboard: () => api.get("/bookings/dashboard/"),
};

export const personesApi = {
  list: () => api.get('/bookings/persones/'),
  get: (id) => api.get(`/bookings/persones/${id}/`),
  create: (data) => api.post('/bookings/persones/', data),
  update: (id, data) => api.patch(`/bookings/persones/${id}/`, data),
  remove: (id) => api.del(`/bookings/persones/${id}/`),
  rendiment: (id) => api.get(`/bookings/persones/${id}/rendiment/`),
};

// àlies per compatibilitat — eliminar quan tots els usos estiguin migrats
export const inquilinsApi = personesApi;

export const perfilsPropietariApi = {
  create: (data) => api.post('/bookings/perfils-propietari/', data),
  update: (id, data) => api.patch(`/bookings/perfils-propietari/${id}/`, data),
};

export const comunicacionsApi = {
  list: (reservaId) => api.get(`/bookings/reserves/${reservaId}/comunicacions/`),
  create: (reservaId, data) => api.post(`/bookings/reserves/${reservaId}/comunicacions/`, data),
  remove: (reservaId, comId) => api.del(`/bookings/reserves/${reservaId}/comunicacions/${comId}/`),
};

export const serveisApi = {
  list: () => api.get("/properties/serveis/"),
};

export const pagamentsApi = {
  listByImmoble: (immobleId) => api.get(`/properties/${immobleId}/pagaments/`),
};

export const usersApi = {
  list:   ()         => api.get('/auth/users/'),
  get:    (id)       => api.get(`/auth/users/${id}/`),
  create: (data)     => api.post('/auth/users/', data),
  update: (id, data) => api.put(`/auth/users/${id}/`, data),
  patch:  (id, data) => api.patch(`/auth/users/${id}/`, data),
  remove: (id)       => api.del(`/auth/users/${id}/`),
};
