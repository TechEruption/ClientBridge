import { useEffect, useState } from "react";
import { api } from "../api";

export default function MailComposer({ enquiry }) {
  const draft = enquiry.email_draft || {};
  const [subject, setSubject] = useState(draft.subject || "");
  const [body, setBody] = useState(draft.body || "");
  const [recipient, setRecipient] = useState(enquiry.company_email || "soumabha015@gmail.com");
  const [editingRecipient, setEditingRecipient] = useState(false);
  const [preview, setPreview] = useState(false);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setSubject(draft.subject || "");
    setBody(draft.body || "");
    setRecipient(enquiry.company_email || "soumabha015@gmail.com");
  }, [enquiry.id]);

  async function send() {
    setSending(true);
    setMessage("");
    try {
      await api(`/api/admin/enquiries/${enquiry.id}/send-mail`, {
        method: "POST",
        body: JSON.stringify({ subject, body, recipient }),
      });
      setMessage("Email sent successfully.");
      setPreview(false);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="panel mail-composer">
      <h2>Mail composer</h2>
      <label>Subject<input value={subject} onChange={(event) => setSubject(event.target.value)} /></label>
      <label>Recipient
        <div className="recipient-row">
          <input value={recipient} disabled={!editingRecipient} onChange={(event) => setRecipient(event.target.value)} />
          <button type="button" onClick={() => setEditingRecipient((value) => !value)}>{editingRecipient ? "Lock" : "Edit recipient"}</button>
        </div>
      </label>
      <label>Message<textarea rows="11" value={body} onChange={(event) => setBody(event.target.value)} /></label>
      <button className="primary-button" onClick={() => setPreview(true)}>Preview email</button>
      {preview && (
        <div className="preview-modal" role="dialog" aria-modal="true">
          <div className="preview-card">
            <header><h3>Email preview</h3><button onClick={() => setPreview(false)}>×</button></header>
            <p><strong>To:</strong> {recipient}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <pre>{body}</pre>
            <button className="primary-button" onClick={send} disabled={sending}>{sending ? "Sending..." : "Confirm and send"}</button>
          </div>
        </div>
      )}
      {message && <p className={message.includes("success") ? "success-text" : "error"}>{message}</p>}
    </section>
  );
}
