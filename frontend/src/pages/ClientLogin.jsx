import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function ClientLogin() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function submit(event) {
    event.preventDefault();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setError("Enter a valid email address.");
      return;
    }
    localStorage.setItem("seallink_client_email", email.trim().toLowerCase());
    navigate("/client");
  }

  return (
    <main className="login-page client-login-page">
      <form className="login-card" onSubmit={submit}>
        <Link className="brand" to="/"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></Link>
        <p className="eyebrow">Client portal</p>
        <h1>Continue with email</h1>
        <p>No registration needed. Use the email for each enquiry.</p>
        <label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@company.com" /></label>
        {error && <p className="error">{error}</p>}
        <button className="primary-button" type="submit">Continue</button>
        <Link className="back-link" to="/">← Choose another portal</Link>
      </form>
    </main>
  );
}
