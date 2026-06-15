// Tiny fetch wrapper. Same-origin, so no base URL needed.
async function apiCall(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }
  if (!res.ok) throw { status: res.status, data };
  return data;
}
window.API = {
  get: (p) => apiCall(p),
  post: (p, body) => apiCall(p, { method: "POST", body: body ? JSON.stringify(body) : null }),
  patch: (p, body) => apiCall(p, { method: "PATCH", body: JSON.stringify(body) }),
};
