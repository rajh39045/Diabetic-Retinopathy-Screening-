import { useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, ClipboardCheck, Eye, ImagePlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card";
import { patientApi, screeningApi } from "../services/api";

const COMPLETED_STATUSES = ["CONFIRMED", "MODIFIED", "RECAPTURE_REQUIRED", "REFERRED"];

const formatDate = (value) => {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleDateString();
};

const gradeLabel = (grade) => grade === null || grade === undefined || grade === "" ? "-" : `Grade ${grade}`;

const statusTone = (status) => {
  if (["CONFIRMED", "MODIFIED"].includes(status)) return "success";
  if (status === "RECAPTURE_REQUIRED") return "warning";
  if (status === "REFERRED") return "danger";
  return "warning";
};

export default function OphthalmologistDashboard() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [screenings, setScreenings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([patientApi.list(), screeningApi.list()])
      .then(([patientsResponse, screeningsResponse]) => {
        setPatients(patientsResponse.data);
        setScreenings(screeningsResponse.data);
      })
      .catch(() => setError("Unable to load the clinical review queue."))
      .finally(() => setLoading(false));
  }, []);

  const patientMap = useMemo(
    () => Object.fromEntries(patients.map(patient => [patient.patient_id, patient])),
    [patients]
  );
  const pending = screenings.filter(screening => screening.status === "PENDING_REVIEW");
  const completed = screenings.filter(screening => COMPLETED_STATUSES.includes(screening.status));
  const newImageCases = screenings.filter(screening => screening.status === "RECAPTURE_REQUIRED");

  return (
    <div className="page ophthalmologist-dashboard">
      <div className="page-title">
        <div>
          <div className="eyebrow">OPHTHALMOLOGY REVIEW WORKSPACE</div>
          <h1>Clinical review dashboard</h1>
          <p className="muted">Review AI-supported retinal screenings and finalize clinical decisions.</p>
        </div>
      </div>

      {error && <div className="auth-error">{error}</div>}

      <div className="stats-grid">
        <Card><div className="stat"><div className="stat-icon"><ClipboardCheck /></div><div><span>Pending reviews</span><strong>{pending.length}</strong><small>Awaiting your review</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><CheckCircle2 /></div><div><span>Completed reviews</span><strong>{completed.length}</strong><small>Final decisions recorded</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><Activity /></div><div><span>Total screenings</span><strong>{screenings.length}</strong><small>All screening cases</small></div></div></Card>
        <Card><div className="stat"><div className="stat-icon"><ImagePlus /></div><div><span>Cases requiring new image</span><strong>{newImageCases.length}</strong><small>Recapture required</small></div></div></Card>
      </div>

      <div className="review-sections">
        <Card title="Pending reviews" subtitle="Cases waiting for ophthalmologist review">
          {loading ? <p className="muted">Loading review queue...</p> : pending.length === 0 ? <p className="muted">No pending reviews.</p> : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Screening / Patient</th><th>Date</th><th>Eye</th><th>AI grade</th><th>Confidence</th><th>Risk</th><th>Image quality</th><th>Status</th><th /></tr></thead>
                <tbody>
                  {pending.map(screening => {
                    const patient = patientMap[screening.patient_id];
                    const ai = screening.ai_prediction || {};
                    return (
                      <tr key={screening.case_id} className="review-row" onClick={() => navigate(`/doctor-review/${screening.case_id}`)}>
                        <td><strong>{screening.case_id}</strong><br /><span>{screening.patient_id} · {patient?.name || "Unknown patient"}</span></td>
                        <td>{formatDate(screening.created_at)}</td><td>{screening.evaluated_eye || "-"}</td>
                        <td><strong>{gradeLabel(ai.dr_grade)}</strong><br /><span>{ai.severity_name || "-"}</span></td>
                        <td>{ai.confidence_percent || "-"}</td><td>{ai.risk || "-"}</td>
                        <td><span className={`badge ${screening.quality?.overall_status === "ACCEPTED" ? "success" : "warning"}`}>{screening.quality?.overall_status || "-"}</span></td>
                        <td><span className={`badge ${statusTone(screening.status)}`}>{screening.status}</span></td>
                        <td><button className="table-link" onClick={(event) => { event.stopPropagation(); navigate(`/doctor-review/${screening.case_id}`); }}>Review</button></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Completed reviews" subtitle="Previously reviewed cases">
          {loading ? <p className="muted">Loading completed reviews...</p> : completed.length === 0 ? <p className="muted">No completed reviews.</p> : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Screening</th><th>Patient</th><th>Screening date</th><th>AI grade</th><th>Final grade</th><th>Decision</th><th>Review date</th><th>Status</th><th /></tr></thead>
                <tbody>
                  {completed.map(screening => {
                    const patient = patientMap[screening.patient_id];
                    const ai = screening.ai_prediction || {};
                    const review = screening.doctor_review || {};
                    return (
                      <tr key={screening.case_id} className="review-row" onClick={() => navigate(`/report/${screening.case_id}`)}>
                        <td><strong>{screening.case_id}</strong></td><td>{patient?.name || screening.patient_id}</td><td>{formatDate(screening.created_at)}</td>
                        <td>{gradeLabel(ai.dr_grade)}</td><td>{gradeLabel(review.final_grade)}</td><td>{review.decision || "-"}</td>
                        <td>{formatDate(review.reviewed_at)}</td><td><span className={`badge ${statusTone(screening.status)}`}>{screening.status}</span></td>
                        <td><button className="table-link" onClick={(event) => { event.stopPropagation(); navigate(`/report/${screening.case_id}`); }}>Open</button></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      <div className="review-note"><Eye size={17} /><span><strong>Clinical decision support</strong> Review the retinal image and explainability evidence before recording a final decision.</span><AlertTriangle size={17} /></div>
    </div>
  );
}