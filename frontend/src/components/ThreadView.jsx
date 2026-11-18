export default function ThreadView({ messages, syncState, onSync }) {
  return (
    <section className="panel thread-panel">
      <div className="thread-heading"><h2>Conversation thread</h2><div><span>Last synced: {syncState?.last_synced ? new Date(syncState.last_synced).toLocaleTimeString() : "Not yet"}</span><button onClick={onSync}>Sync now</button></div></div>
      {syncState?.error && <p className="error sync-error">{syncState.error}</p>}
      <div className="thread">
        {messages.length === 0 && <p className="chat-empty">No messages in this thread.</p>}
        {messages.map((message) => (
          <article className={`thread-message ${message.direction}`} key={message.id}>
            <header><strong>{message.direction === "out" ? "Sent" : "Client reply"}</strong>{message.unread && <span className="unread-badge">Unread</span>}<time>{new Date(message.timestamp).toLocaleString()}</time></header>
            {message.subject && <b>{message.subject}</b>}
            <pre>{message.body}</pre>
          </article>
        ))}
      </div>
    </section>
  );
}
