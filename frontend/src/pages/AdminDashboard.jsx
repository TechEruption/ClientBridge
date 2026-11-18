import { useEffect, useState } from "react";
import { api } from "../api";
import AdminShell from "../components/AdminShell";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  useEffect(() => { api("/api/admin/stats").then(setStats).catch(() => {}); }, []);
  if (!stats) return <AdminShell><p className="loading">Loading dashboard...</p></AdminShell>;
  const cards = [
    ["Total enquiries", stats.total],
    ["New today", stats.new_today],
    ["Unread replies", stats.unread_replies],
    ["Stages skipped", stats.total_stages_skipped],
  ];
  return (
    <AdminShell>
      <header className="admin-title"><div><p className="eyebrow">Operations overview</p><h1>Dashboard</h1></div></header>
      <div className="metric-grid">
        {cards.map(([label, value]) => <article className="metric-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}
      </div>
      <section className="dashboard-grid">
        <article className="panel">
          <h2>Enquiries by type</h2>
          {Object.entries(stats.per_type).map(([key, value]) => <div className="bar-row" key={key}><span>{key.replace("_", " ")}</span><div><i style={{ width: `${Math.max(8, value * 20)}%` }} /></div><strong>{value}</strong></div>)}
        </article>
        <article className="panel">
          <h2>Enquiry statuses</h2>
          {Object.entries(stats.per_status).map(([key, value]) => <div className="bar-row" key={key}><span>{key.replace("_", " ")}</span><div><i style={{ width: `${Math.max(8, value * 20)}%` }} /></div><strong>{value}</strong></div>)}
        </article>
      </section>
    </AdminShell>
  );
}
