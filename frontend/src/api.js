export const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function api(path, { method = 'GET', body, auth = false, headers: customHeaders } = {}) {
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  const headers = new Headers(customHeaders || {});

  if (!isFormData && body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (auth) {
    const token = localStorage.getItem('token');
    if (token) headers.set('Authorization', `Bearer ${token}`);
  }

  let requestBody;
  if (isFormData) {
    requestBody = body;
  } else if (body === undefined) {
    requestBody = undefined;
  } else if (typeof body === 'string') {
    requestBody = body;
  } else {
    requestBody = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: requestBody,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}