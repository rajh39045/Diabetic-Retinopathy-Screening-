
import { useEffect, useState } from "react";
import { Download, Printer, CheckCircle2, ArrowLeft } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { reportApi } from "../services/api";

export default function FinalReport() {
  const { patientId: caseId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    reportApi.get(caseId)
      .then(({data}) => setReport(data))
      .catch(err => setError(err.response?.data?.detail || "Unable to load report."));
  }, [caseId]);

  const print = () => window.print();

  const ai = report?.screening?.ai_prediction || {};
  const review = report?.doctor_review;

  return (
    <div className="page">
      <div className="page-title no-print">
        <div>
          <div className="eyebrow">STEP 5 OF 5 · FINAL REPORT</div>
          <h1>Screening report</h1>
          <p className="muted">Case {caseId}</p>
        </div>
        <div className="button-group">
          <Button variant="secondary" onClick={print}><Printer size={17}/> Print</Button>
          <a
            className="btn btn-primary"
            href={reportApi.pdfUrl(caseId)}
            target="_blank"
            rel="noreferrer"
          >
            <Download size={17}/> Download PDF
          </a>
        </div>
      </div>

      {error && <div className="auth-error">{error}</div>}

      <div className="report-sheet">
        <div className="report-header">
          <div><strong>RETINA-XAI</strong><span>Explainable retinal screening report</span></div>
          <span className="badge success"><CheckCircle2 size={15}/> {review ? "Clinician reviewed" : "AI result"}</span>
        </div>

        <div className="report-meta">
          <div><span>Patient ID</span><strong>{report?.patient?.patient_id || "-"}</strong></div>
          <div><span>Patient</span><strong>{report?.patient?.name || "-"}</strong></div>
          <div><span>Eye</span><strong>{report?.screening?.evaluated_eye || "-"}</strong></div>
          <div><span>Status</span><strong>{report?.screening?.status || "-"}</strong></div>
        </div>

        <div className="report-result">
          <div>
            <span>AI SCREENING RESULT</span>
            <strong>{ai.severity_name || "Not available"}</strong>
            <p>{ai.recommendation || "No recommendation available."}</p>
          </div>
          <div className="score-ring small-ring">
            <strong>{ai.confidence_percent || "-"}</strong>
            <span>confidence</span>
          </div>
        </div>

        <div className="report-section">
          <h3>AI findings</h3>
          <ul>
            <li>Model status: {ai.model_status || "Not available"}.</li>
            <li>DR grade: {ai.dr_grade ?? "-"}</li>
            <li>Risk: {ai.risk || "-"}</li>
          </ul>
        </div>

        <div className="report-section">
          <h3>Clinician decision</h3>
          <p>{review?.decision || "Pending clinician review."}</p>
          {review?.doctor_notes && <p>{review.doctor_notes}</p>}
        </div>

        <div className="report-section">
          <h3>Clinical disclaimer</h3>
          <p>This report is decision support generated using an AI-assisted screening workflow. It is not a standalone diagnosis.</p>
        </div>

        <div className="signature"><div>Clinician signature</div><div>Date</div></div>
      </div>

      <div className="form-actions no-print">
        <Button variant="secondary" onClick={() => navigate("/dashboard")}><ArrowLeft size={17}/> Return to dashboard</Button>
      </div>
    </div>
  );
}
