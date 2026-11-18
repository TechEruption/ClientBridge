import { useState } from "react";
import { api } from "../api";

export default function ChatWidget({ sessionId }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [typing, setTyping] = useState(false);
  const [phoneVisible, setPhoneVisible] = useState(false);

  async function send(event) {
    event.preventDefault();
    if (!message.trim()) return;
    const text = message.trim();
    setMessage("");
    setHistory((current) => [...current, { role: "client", content: text }]);
    setTyping(true);
    try {
      const result = await api("/api/chat", { method: "POST", body: JSON.stringify({ session_id: sessionId, message: text }) });
      setHistory((current) => [...current, { role: "bot", content: result.reply }]);
      setPhoneVisible(result.number_given);
    } catch (error) {
      setHistory((current) => [...current, { role: "bot", content: error.message }]);
    } finally {
      setTyping(false);
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <section className="chat-panel" aria-label="ClientBridge assistant">
          <header><div><strong>ClientBridge Assistant</strong><span>Industrial product guidance</span></div><button onClick={() => setOpen(false)} aria-label="Close chat">×</button></header>
          <div className="chat-history">
            {history.length === 0 && <p className="chat-empty">Ask about products, industries or the enquiry form.</p>}
            {history.map((item, index) => <div className={`chat-bubble ${item.role}`} key={index}>{item.content}</div>)}
            {typing && <div className="chat-bubble bot typing"><i /><i /><i /></div>}
          </div>
          {phoneVisible && <a className="call-sales" href="tel:1234567891">Call sales: 1234567891</a>}
          <form onSubmit={send}>
            <input value={message} onChange={(event) => setMessage(event.target.value)} maxLength="500" placeholder="Type a message..." aria-label="Chat message" />
            <button type="submit" aria-label="Send message">Send</button>
          </form>
        </section>
      )}
      <button className="chat-toggle" onClick={() => setOpen((value) => !value)} aria-label="Open chat">
        <span className="chat-icon">◫</span>
      </button>
    </div>
  );
}
