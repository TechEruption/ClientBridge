import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import AdminShell from "../components/AdminShell";
import MailComposer from "../components/MailComposer";
import ThreadView from "../components/ThreadView";
import { clientProvidedData, downloadClientJson } from "../clientExport";

export default function AdminEnquiryDetail() {
  const { id } = useParams();
  const [enquiry, setEnquiry] = useState(null);
  const [syncState, setSyncState] = useState(null);
  const [note, setNote] = useState("");
  const [reply, setReply] = useState("");
  const [status, setStatus] = useState("");
  const [assistantPrompt, setAssistantPrompt] = useState("");

  async function load() {
    const data = await api(`/api/admin/enquiries/${id}`);
    setEnquiry(data);
    setStatus(data.status);
  }

  useEffect(() => { load().catch(() => {}); const timer = setInterval(load, 30000); return () => clearInterval(timer); }, [id]);

  async function patch(payload) {
    const updated = await api(`/api/admin/enquiries/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    setEnquiry(updated);
  }

  async function syncNow() {
    const result = await api("/api/admin/sync-now", { method: "POST" });
    setSyncState(result);
    await load();
  }

  async function generateAssist() {
    const result = await api(`/api/admin/enquiries/${id}/assist`, {
      method: "POST",
      body: JSON.stringify({ instruction: assistantPrompt }),
    });
    setReply(result.body);
  }

  async function sendReply(event) {
    event.preventDefault();
    if (!reply.trim()) return;
    const subject = enquiry.email_draft?.subject || `[${id}] Re: Your enquiry`;
    await api(`/api/admin/enquiries/${id}/send-mail`, { method: "POST", body: JSON.stringify({ subject, body: reply, recipient: enquiry.company_email }) });
    setReply("");
    await load();
  }

  function downloadJson() {
    downloadClientJson(`${enquiry.id}-client-data.json`, clientProvidedData(enquiry));
  }

  if (!enquiry) return <AdminShell><p className="loading">Loading enquiry...</p></AdminShell>;

  return (
    <AdminShell>
      <header className="admin-title detail-title">
        <div><Link className="back-link" to="/admin/enquiries">← Back to enquiries</Link><p className="eyebrow">Enquiry {enquiry.id}</p><h1>{enquiry.company_name}</h1></div>
        <div className="detail-actions"><span className={`type-label ${enquiry.enquiry_type}`}>{enquiry.enquiry_type.replace("_", " ")}</span><button className="download-button" onClick={downloadJson}>Download client JSON</button></div>
      </header>

      <div className="detail-grid">
        <section className="panel client-details">
          <h2>Client details</h2>
          <dl>
            <dt>Contact</dt><dd>{enquiry.name} · {enquiry.designation}</dd>
            <dt>Email</dt><dd>{enquiry.company_email}</dd>
            <dt>Phone</dt><dd>{enquiry.phone}</dd>
            <dt>Industry</dt><dd>{enquiry.industry}</dd>
            <dt>Products</dt><dd>{enquiry.product_interest?.join(", ")}</dd>
            {enquiry.referred_by && <><dt>Referred by</dt><dd>{enquiry.referred_by}</dd></>}
            {enquiry.previous_order_ref && <><dt>Previous order</dt><dd>{enquiry.previous_order_ref}</dd></>}
            {enquiry.quantity && <><dt>Quantity</dt><dd>{enquiry.quantity}</dd></>}
            {enquiry.current_product_used && <><dt>Current product</dt><dd>{enquiry.current_product_used}</dd></>}
            {enquiry.new_product_needed && <><dt>New product needed</dt><dd>{enquiry.new_product_needed}</dd></>}
          </dl>
          <h3>Enquiry message</h3><p>{enquiry.message}</p>
          <h3>Auto-generated summary</h3><p>{enquiry.auto_summary}</p>
        </section>

        <section className="panel admin-controls">
          <h2>Admin controls</h2>
          <label>Status
            <select value={status} onChange={(event) => { setStatus(event.target.value); patch({ status: event.target.value }); }}>
              <option>new</option><option>in_progress</option><option>on_hold</option><option>closed</option>
            </select>
          </label>
          <label>Internal note<textarea rows="4" value={note} onChange={(event) => setNote(event.target.value)} /></label>
          <button onClick={() => { patch({ internal_note: note }); setNote(""); }}>Save note</button>
        </section>

        <MailComposer enquiry={enquiry} />
        <div className="thread-column">
          <ThreadView messages={enquiry.messages || []} syncState={syncState} onSync={syncNow} />
          <form className="panel reply-box" onSubmit={sendReply}>
            <h2>AI or human reply</h2>
            <div className="assistant-controls">
              <input value={assistantPrompt} onChange={(event) => setAssistantPrompt(event.target.value)} placeholder="Ask the AI to draft a reply..." />
              <button type="button" onClick={generateAssist}>Generate draft</button>
            </div>
            <textarea rows="5" value={reply} onChange={(event) => setReply(event.target.value)} placeholder="Write a reply..." />
            <button className="primary-button" type="submit">Send in Gmail thread</button>
          </form>
        </div>

        {enquiry.chat && (
          <section className="panel chat-transcript">
            <h2>Chatbot transcript</h2>
            {enquiry.chat.messages.map((item, index) => <p className={`transcript-${item.role}`} key={index}><strong>{item.role === "client" ? "Client" : "Assistant"}:</strong> {item.content}</p>)}
          </section>
        )}
      </div>
    </AdminShell>
  );
}
