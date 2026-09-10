
import { Activity, ClipboardList, FileText, LayoutDashboard, UserPlus } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/patients/new", label: "New patient", icon: UserPlus },
  { to: "/dashboard", label: "Screenings", icon: Activity },
  { to: "/dashboard", label: "Patients", icon: ClipboardList },
  { to: "/dashboard", label: "Reports", icon: FileText },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="side-label">WORKSPACE</div>
      <nav>
        {items.map(({to,label,icon:Icon}) => (
          <NavLink key={label} to={to} className={({isActive}) => isActive ? "side-link active" : "side-link"}>
            <Icon size={18}/><span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="side-footer">
        <div className="status-dot"/>
        <div><strong>API service</strong><span>Connected when backend is running</span></div>
      </div>
    </aside>
  );
}
