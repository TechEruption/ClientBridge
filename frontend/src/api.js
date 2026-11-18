const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const API = (configuredApiUrl || (import.meta.env.DEV ? "http://localhost:8000" : "")).replace(/\/$/, "");

export async function api(path, options = {}) {
  if (!API) {
    throw new Error("Backend URL is not configured. Set VITE_API_URL to your deployed backend URL in Netlify.");
  }
  const token = localStorage.getItem("seallink_admin_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}
