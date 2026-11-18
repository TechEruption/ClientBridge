import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  async function submit(event) {
    event.preventDefault();
    try {
      const result = await api("/api/admin/login", { method: "POST", body: JSON.stringify({ email }) });
      localStorage.setItem("seallink_admin_token", result.token);
      navigate("/admin");
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="brand"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></div>
        <p className="eyebrow">Private administration</p>
        <h1>Admin sign in</h1>
        <label>Admin email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="admin@company.com" /></label>
        {error && <p className="error">{error}</p>}
        <button className="primary-button" type="submit">Sign in</button>
        <Link className="back-link" to="/">← Back to client/admin selection</Link>
      </form>
    </main>
  );
}
