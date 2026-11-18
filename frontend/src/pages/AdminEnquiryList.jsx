import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import AdminShell from "../components/AdminShell";
import { clientProvidedData, downloadClientJson } from "../clientExport";

const TABS = [
  ["", "All"],
  ["new_client", "New Customer"],
  ["referral", "Referral"],
  ["rebuy", "Repeat Order"],
  ["new_product", "New Product"],
];

export default function AdminEnquiryList() {
  const [items, setItems] = useState([]);
  const [tab, setTab] = useState("");
  const [stage, setStage] = useState("");
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");

  async function load() {
    const params = new URLSearchParams();
    if (tab) params.set("type", tab);
    if (stage) params.set("stage", stage);
    if (status) params.set("status", status);
    if (search) params.set("search", search);
    setItems(await api(`/api/admin/enquiries?${params}`));
  }
  useEffect(() => { load().catch(() => {}); }, [tab, stage, status]);
  async function remove(enquiry) {
    if (!window.confirm(`Remove ${enquiry.id} and all related messages?`)) return;
    await api(`/api/admin/enquiries/${enquiry.id}`, { method: "DELETE" });
    await load();
  }
  function downloadOne(enquiry) {
    downloadClientJson(`${enquiry.id}-client-data.json`, clientProvidedData(enquiry));
  }
  function downloadAll() {
    downloadClientJson(
      tab ? `enquiries-${tab}.json` : "all-enquiries.json",
      items.map(clientProvidedData)
    );
  }

  return (
    <AdminShell>
      <header className="admin-title"><div><p className="eyebrow">Client pipeline</p><h1>Enquiries</h1></div></header>
      <div className="tabs">
        {TABS.map(([value, label]) => <button className={tab === value ? "active" : ""} key={value} onClick={() => setTab(value)}>{label}</button>)}
      </div>
      <div className="filters">
        <input value={search} onChange={(event) => setSearch(event.target.value)} onKeyDown={(event) => event.key === "Enter" && load()} placeholder="Search enquiries" />
        <select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option><option>new</option><option>in_progress</option><option>on_hold</option><option>closed</option></select>
        <button onClick={load}>Search</button>
        <button className="download-button" onClick={downloadAll}>Download {tab ? "filtered" : "all"} JSON</button>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Enquiry</th><th>Company</th><th>Type</th><th>Status</th><th>Export</th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td><Link to={`/admin/enquiries/${item.id}`}>{item.id}<br /><small>{item.name}</small></Link>{item.has_unread_reply && <span className="unread-badge">Unread</span>}</td>
                <td>{item.company_name}</td>
                <td><span className={`type-label ${item.enquiry_type}`}>{item.enquiry_type.replace("_", " ")}</span></td>
                <td>{item.status} <button className="remove-button" onClick={() => remove(item)}>Remove</button></td>
                <td><button className="download-row-button" onClick={() => downloadOne(item)}>Download JSON</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminShell>
  );
}
