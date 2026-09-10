
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import OphthalmologistDashboard from "./pages/OphthalmologistDashboard";
import PatientRegistration from "./pages/PatientRegistration";
import ImageCapture from "./pages/ImageCapture";
import ImageQuality from "./pages/ImageQuality";
import ScreeningResult from "./pages/ScreeningResult";
import Explainability from "./pages/Explainability";
import DoctorReview from "./pages/DoctorReview";
import FinalReport from "./pages/FinalReport";

function AppShell({ children }) {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}

function DashboardRoute() {
  const { user } = useAuth();
  return user?.role === "OPHTHALMOLOGIST" ? <OphthalmologistDashboard /> : <Dashboard />;
}

function RoleRoute({ roles, children }) {
  const { user } = useAuth();
  return roles.includes(user?.role) ? children : <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<AppShell><DashboardRoute /></AppShell>} />
        <Route path="/patients/new" element={<AppShell><PatientRegistration /></AppShell>} />
        <Route path="/capture/:patientId" element={<AppShell><ImageCapture /></AppShell>} />
        <Route path="/quality/:patientId" element={<AppShell><ImageQuality /></AppShell>} />
        <Route path="/screening/:patientId" element={<AppShell><ScreeningResult /></AppShell>} />
        <Route path="/explainability/:patientId" element={<AppShell><Explainability /></AppShell>} />
        <Route path="/doctor-review/:patientId" element={<AppShell><RoleRoute roles={["OPHTHALMOLOGIST"]}><DoctorReview /></RoleRoute></AppShell>} />
        <Route path="/report/:patientId" element={<AppShell><FinalReport /></AppShell>} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
