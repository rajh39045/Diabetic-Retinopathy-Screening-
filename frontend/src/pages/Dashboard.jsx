
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, Plus, Search, Users, Activity, AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { patientApi, screeningApi } from "../services/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [screenings, setScreenings] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [p, s] = await Promise.all([
        patientApi.list(),
        screeningApi.list(),
      ]);
      setPatients(p.data);
      setScreenings(s.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const patientMap = useMemo(
    () => Object.fromEntries(patients.map(p => [p.patient_id, p])),
    [patients]
  );

  const filtered = screenings.filter(s => {
    const patient = patientMap[s.patient_id];
    const haystack = `${s.case_id} ${s.patient_id} ${patient?.name || ""}`.toLowerCase();
    return haystack.includes(query.toLowerCase());
  });

  const pending = screenings.filter(s => s.status === "PENDING_REVIEW").length;
  const completed = screenings.filter(s => ["CONFIRMED","MODIFIED","REFERRED"].includes(s.status)).length;

  return (
    <div className="page">
      <div className="page-title">
        <div>
          <div className="eyebrow">CLINICAL OVERVIEW</div>
          <h1>Screening dashboard</h1>
          <p className="muted">Live data from FastAPI + MongoDB.</p>
        </div>
        <Button onClick={() => navigate("/patients/new")}><Plus size={18}/> New screening</Button>
      </div>

      <div className="stats-grid">
        <Card><div className="stat"><div className="stat-icon"><Users/></div><div><span>Total patients</span><strong>{patients.length}</strong><small>From MongoDB</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><Activity/></div><div><span>Total screenings</span><strong>{screenings.length}</strong><small>All cases</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><AlertTriangle/></div><div><span>Needs review</span><strong>{pending}</strong><small>AI cases</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><CheckCircle2/></div><div><span>Completed</span><strong>{completed}</strong><small>Clinician reviewed</small></div></div></Card>
      </div>

      <div className="dashboard-grid">
        <Card title="Recent screenings" subtitle="Loaded from the backend">
          <div className="search-box"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search case, patient ID or name"/></div>

          {loading ? <p className="muted">Loading...</p> : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Case</th><th>Patient</th><th>Eye</th><th>AI result</th><th>Status</th><th/></tr></thead>
                <tbody>
                  {filtered.slice(0, 20).map(s => {
                    const patient = patientMap[s.patient_id];
                    const ai = s.ai_prediction;
                    return (
                      <tr key={s.case_id}>
                        <td><strong>{s.case_id}</strong><br/><span>{s.patient_id}</span></td>
                        <td>{patient?.name || "-"}</td>
                        <td>{s.evaluated_eye}</td>
                        <td><span className={`badge ${ai?.dr_grade >= 2 ? "warning" : "success"}`}>{ai?.severity_name || "Not run"}</span></td>
                        <td>{s.status}</td>
                        <td><button className="table-link" onClick={() => navigate(`/screening/${s.case_id}`)}>Open</button></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Screening workflow" subtitle="API-backed clinical flow">
          <div className="workflow">
            {[
              ["01","Register patient","Save patient + screening case"],
              ["02","Upload image","Store fundus image + metadata"],
              ["03","AI screening","Stable API contract for DL model"],
              ["04","Explain & review","Grad-CAM + clinician review"],
              ["05","Final report","MongoDB record + PDF"]
            ].map((x,i) => (
              <div className="workflow-item" key={x[0]}>
                <span>{x[0]}</span>
                <div><strong>{x[1]}</strong><small>{x[2]}</small></div>
                {i < 4 && <ArrowRight size={15}/>}
              </div>
            ))}
          </div>
          <Button className="full" onClick={() => navigate("/patients/new")}>Start workflow</Button>
        </Card>
      </div>
    </div>
  );
}
