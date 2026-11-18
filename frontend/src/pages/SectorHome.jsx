import { Link } from "react-router-dom";

export default function SectorHome() {
  return (
    <main className="sector-page">
      <div className="sector-brand">
        <div className="brand"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></div>
      </div>
      <section className="sector-grid">
        <Link className="sector-card client-sector" to="/client/login">
          <span className="sector-index">01</span>
          <div>
            <p className="eyebrow">For buyers</p>
            <h1>Client</h1>
            <p>Submit a requirement or continue an existing enquiry with your email.</p>
            <strong>Enter client portal →</strong>
          </div>
        </Link>
        <Link className="sector-card admin-sector" to="/admin/login">
          <span className="sector-index">02</span>
          <div>
            <p className="eyebrow">For sales team</p>
            <h1>Admin</h1>
            <p>Review enquiries and respond to clients.</p>
            <strong>Enter admin portal →</strong>
          </div>
        </Link>
      </section>
      <footer>Prototype concept. Not an official company website.</footer>
    </main>
  );
}
