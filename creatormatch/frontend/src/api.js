const API_BASE = '';

function getToken() { return localStorage.getItem('token'); }

export async function api(method, path, body) {
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken() || ''}`
    }
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}/api${path}`, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data.data;
}

export const get = (p) => api('GET', p);
export const post = (p, b) => api('POST', p, b);
export const patch = (p, b) => api('PATCH', p, b);

export function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location = '/'; }
export function isAuth() { return !!getToken(); }
export function getUser() { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } }
