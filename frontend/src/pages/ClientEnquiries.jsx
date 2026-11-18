import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { api } from "../api";

export default function ClientEnquiries() {
  const email = localStorage.getItem("seallink_client_email");
  const { id } = useParams();
  const [items, setItems] = useState([]);
  const [detail, setDetail] = useState(null);
  const [reply, setReply] = useState("");

  async function load() {
    if (id) {
      setDetail(await api(`/api/client/enquiries/${encodeURIComponent(id)}?email=${encodeURIComponent(email)}`));
    } else {
      setItems(await api(`/api/client/enquiries?email=${encodeURIComponent(email)}`));
    }
  }

  useEffect(() => { if (email) load().catch(() => setDetail(null)); const timer = setInterval(() => { if (email) load().catch(() => {}); }, 30000); return () => clearInterval(timer); }, [email, id]);

  async function send(event) {
    event.preventDefault();
    if (!reply.trim()) return;
    await api(`/api/client/enquiries/${id}/reply`, {
      method: "POST",
      body: JSON.stringify({ email, body: reply }),
    });
    setReply("");
    await load();
  }

  if (!email) return <Navigate to="/client/login" replace />;

  return (
    <main className="client-inbox">
      <header className="client-inbox-header"><Link className="brand" to="/"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></Link><div className="client-header-actions"><Link to="/client">← Back to client page</Link><span>{email}</span></div></header>
      {id ? (
        detail ? (
          <section className="client-thread-layout">
            <aside>
              <Link to="/client/enquiries">← All enquiries</Link>
              <p className="eyebrow">Enquiry</p>
              <h1>{detail.id}</h1>
              <p>{detail.company_name}</p>
              <dl><dt>Product</dt><dd>{detail.product_interest?.join(", ")}</dd><dt>Message</dt><dd>{detail.message}</dd></dl>
            </aside>
            <div>
              <section className="panel client-thread">
                <h2>Conversation</h2>
                {detail.messages?.map((message) => (
                  <article className={`thread-message ${message.direction}`} key={message.id}>
                    <header><strong>{message.direction === "out" ? "ClientBridge" : "You"}</strong><time>{new Date(message.timestamp).toLocaleString()}</time></header>
                    <pre>{message.body}</pre>
                  </article>
                ))}
              </section>
              <form className="panel reply-box" onSubmit={send}>
                <h2>Reply</h2>
                <textarea rows="5" value={reply} onChange={(event) => setReply(event.target.value)} placeholder="Write a reply..." />
                <button className="primary-button" type="submit">Send by email</button>
              </form>
            </div>
          </section>
        ) : <p className="loading">Loading enquiry...</p>
      ) : (
        <section className="client-enquiry-list">
          <p className="eyebrow">My enquiries</p>
          <h1>Enquiry inbox</h1>
          {items.map((item) => (
            <Link className="client-enquiry-row" key={item.id} to={`/client/enquiries/${item.id}`}>
              <div><strong>{item.id}</strong><span>{item.company_name}</span></div>
              <p>{item.product_interest?.join(", ")}</p>
              {item.has_unread_reply && <b>Replied</b>}
            </Link>
          ))}
          {items.length === 0 && <p>No enquiries found for {email}.</p>}
        </section>
      )}
    </main>
  );
}
