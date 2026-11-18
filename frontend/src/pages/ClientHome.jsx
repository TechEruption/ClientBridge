import { useMemo } from "react";
import { Navigate } from "react-router-dom";
import EnquiryForm from "../components/EnquiryForm";
import ChatWidget from "../components/ChatWidget";

export default function ClientHome() {
  const clientEmail = localStorage.getItem("seallink_client_email");
  const sessionId = useMemo(() => sessionStorage.getItem("seallink_chat_session") || (() => {
    const value = `chat-${crypto.randomUUID()}`;
    sessionStorage.setItem("seallink_chat_session", value);
    return value;
  })(), []);
  if (!clientEmail) return <Navigate to="/client/login" replace />;

  return (
    <div className="client-page">
      <header className="site-header">
        <a className="brand" href="/" aria-label="ClientBridge home"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></a>
        <div className="header-actions"><a className="header-link" href="#enquiry">Make an enquiry</a><a className="header-link" href="/client/enquiries">My enquiries</a><a className="back-link" href="/">← Back</a></div>
      </header>
      <main>
        <section className="hero">
          <div>
            <p className="eyebrow">Industrial sealing solutions · Kolkata</p>
            <h1>Sealing expertise for demanding operations.</h1>
            <p>Tell us what your application needs. Existing customers get a fast-track path straight to the right stage.</p>
            <a className="primary-button" href="#enquiry">Start an enquiry</a>
          </div>
          <div className="hero-mark" aria-hidden="true"><span>🤝</span><b>CLIENT<br />BRIDGE</b></div>
        </section>
        <section className="form-section" id="enquiry">
          <div className="section-heading">
            <p className="eyebrow">B2B enquiry portal</p>
            <h2>Tell us about your requirement</h2>
          </div>
          <EnquiryForm sessionId={sessionId} />
        </section>
      </main>
      <footer>Prototype concept. Not an official company website.</footer>
      <ChatWidget sessionId={sessionId} />
    </div>
  );
}
