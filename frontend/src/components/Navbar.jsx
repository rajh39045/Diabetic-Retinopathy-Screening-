import { Bell, CircleUserRound, LogOut, Menu, Stethoscope } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-mark"><Stethoscope size={20} /></div>
        <div><strong>RETINA-XAI</strong><span>Explainable retinal screening</span></div>
      </div>
      <div className="nav-actions">
        <button className="icon-btn" aria-label="Notifications"><Bell size={19}/><i /></button>
        <div className="user-chip">
          <CircleUserRound size={28} />
          <div><strong>{user?.name || "Clinician"}</strong><span>{user?.role || "Clinical user"}</span></div>
        </div>
        <button className="icon-btn" onClick={logout} title="Sign out"><LogOut size={18}/></button>
      </div>
    </header>
  );
}