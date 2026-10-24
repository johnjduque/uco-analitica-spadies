// Cliente HTTP único de la aplicación.
// - Agrega el token JWT en cada petición (cabecera Authorization).
// - Ante 401 cierra la sesión y vuelve al inicio de sesión.
// - Normaliza los mensajes de error del backend.

const API_BASE =
  typeof window !== 'undefined' && window.location.port === '5173'
    ? `http://${window.location.hostname || '127.0.0.1'}:8000`
    : '';

const TOKEN_KEY = 'uco.token';
const USER_KEY = 'uco.user';

let unauthorizedHandler = null;

export const session = {
  get token() {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  get user() {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); } catch { return null; }
  },
  save(token, user) {
    try {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch { /* almacenamiento no disponible */ }
  },
  clear() {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch { /* almacenamiento no disponible */ }
  },
};

export function onUnauthorized(handler) {
  unauthorizedHandler = handler;
}

export class ApiError extends Error {
  constructor(message, status, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request(path, { method = 'GET', body, form, raw = false, auth = true } = {}) {
  const headers = {};
  const token = session.token;
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) payload = form;
  else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${API_BASE}/api${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError('No fue posible conectar con el servidor.', 0, 'NETWORK');
  }

  if (res.status === 401 && auth && path !== '/auth/login') {
    session.clear();
    if (unauthorizedHandler) unauthorizedHandler();
  }
  if (!res.ok) {
    let msg = `Error ${res.status}`;
    let code;
    try {
      const data = await res.json();
      msg = data?.error?.message || data?.detail || data?.message || msg;
      code = data?.error?.code;
      if (data?.error?.trace_id && res.status >= 500) msg += ` (código de seguimiento: ${data.error.trace_id})`;
    } catch { /* respuesta sin JSON */ }
    throw new ApiError(msg, res.status, code);
  }
  if (raw) return res;
  return res.status === 204 ? null : res.json();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  del: (path) => request(path, { method: 'DELETE' }),
  upload: (path, form) => request(path, { method: 'POST', form }),
  login: (username, password) => request('/auth/login', { method: 'POST', body: { username, password }, auth: false }),

  // Descarga un archivo protegido (con token) y lo guarda en el equipo.
  async download(path, fallbackName) {
    const res = await request(path, { raw: true });
    const blob = await res.blob();
    const cd = res.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="?([^"]+)"?/);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = match ? match[1] : fallbackName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },
};

export function qs(params) {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') p.append(k, v);
  });
  const s = p.toString();
  return s ? `?${s}` : '';
}
