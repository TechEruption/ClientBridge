const API = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function api(path, options = {}) {
  const token = localStorage.getItem("seallink_admin_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}
