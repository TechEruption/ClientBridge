import { Navigate, Route, Routes } from "react-router-dom";
import ClientHome from "./pages/ClientHome";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminEnquiryList from "./pages/AdminEnquiryList";
import AdminEnquiryDetail from "./pages/AdminEnquiryDetail";
import SectorHome from "./pages/SectorHome";
import ClientLogin from "./pages/ClientLogin";
import ClientEnquiries from "./pages/ClientEnquiries";

function Protected({ children }) {
  return localStorage.getItem("seallink_admin_token") ? children : <Navigate to="/admin/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<SectorHome />} />
      <Route path="/client/login" element={<ClientLogin />} />
      <Route path="/client" element={<ClientHome />} />
      <Route path="/client/enquiries" element={<ClientEnquiries />} />
      <Route path="/client/enquiries/:id" element={<ClientEnquiries />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<Protected><AdminDashboard /></Protected>} />
      <Route path="/admin/enquiries" element={<Protected><AdminEnquiryList /></Protected>} />
      <Route path="/admin/enquiries/:id" element={<Protected><AdminEnquiryDetail /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
