import { Link, useNavigate } from "react-router-dom";

export default function AdminShell({ children }) {
  const navigate = useNavigate();
  function logout() {
    localStorage.removeItem("seallink_admin_token");
    navigate("/admin/login");
  }
  return (
    <div className="admin-page">
      <aside className="admin-sidebar">
        <Link className="brand" to="/admin"><span aria-hidden="true">🤝</span><strong>ClientBridge</strong></Link>
        <nav>
          <Link to="/admin">Dashboard</Link>
          <Link to="/admin/enquiries">Enquiries</Link>
          <a href="/client/login" target="_blank" rel="noreferrer">View client page ↗</a>
        </nav>
        <button onClick={logout}>Sign out</button>
      </aside>
      <main className="admin-main">{children}</main>
    </div>
  );
}
