
import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, Download, FileCheck2, Image as ImageIcon, ShieldCheck } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { reportApi, reviewApi, screeningApi, toAbsoluteUrl } from "../services/api";
import { useAuth } from "../context/AuthContext";

const decisions = [
  ["CONFIRM_AI", "Confirm AI recommendation"],
  ["MODIFY_GRADE", "Modify AI grade"],
  ["REQUEST_NEW_IMAGE", "Request new image"],
  ["REFER_PATIENT", "Refer patient"],
];

export default function DoctorReview() {
  const { patientId: caseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [report, setReport] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [decision, setDecision] = useState("CONFIRM_AI");
  const [notes, setNotes] = useState("");
  const [finalGrade, setFinalGrade] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([reportApi.get(caseId), screeningApi.comparison(caseId)])
      .then(([reportResponse, comparisonResponse]) => {
        const data = reportResponse.data;
        setReport(data);
        setComparison(comparisonResponse.data);
        if (data.doctor_review) {
          setDecision(data.doctor_review.decision || "CONFIRM_AI");
          setNotes(data.doctor_review.doctor_notes || "");
          setFinalGrade(data.doctor_review.final_grade || "");
        }
      })
      .catch(err => setError(err.response?.data?.detail || "Unable to load this screening case."))
      .finally(() => setLoadingReport(false));
  }, [caseId]);

  const submit = async () => {
    setLoading(true);
    setError("");

    try {
      await reviewApi.create({
        screening_id: caseId,
        doctor_name: user?.name || "Clinical Reviewer",
        decision,
        final_grade: finalGrade || null,
        doctor_notes: notes || null,
      });
      const { data } = await reportApi.get(caseId);
      setReport(data);
      const comparisonResponse = await screeningApi.comparison(caseId);
      setComparison(comparisonResponse.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to save review.");
    } finally {
      setLoading(false);
    }
  };

  const screening = report?.screening || {};
  const patient = report?.patient || {};
  const ai = screening.ai_prediction || {};
  const quality = screening.quality || {};
  const images = screening.images || {};
  const originalImage = images[screening.evaluated_eye]?.file_url || images.OD?.file_url || images.OS?.file_url;
  const gradcamImage = ai.gradcam_url || ai.gradcam_urls?.overlay;
  const lesionImage = ai.lesion_evidence_url;
  const qualityRejected = screening.status === "QUALITY_REJECTED" || quality.final_status === "REJECTED";
  const completed = !!report?.doctor_review;

  const metricRows = [
    ["Blur score", quality.blur_score ?? quality.focus_sharpness], ["Blur status", quality.blur_status],
    ["Brightness score", quality.brightness_score ?? quality.brightness], ["Brightness status", quality.brightness_status],
    ["FOV ratio", quality.fov_ratio ?? quality.field_of_view], ["FOV status", quality.fov_status],
    ["Visibility ratio", quality.visibility_ratio ?? quality.vessel_visibility], ["Visibility status", quality.visibility_status],
    ["Final quality status", quality.final_status ?? quality.overall_status],
  ];

  if (loadingReport) return <div className="page"><div className="loader-wrap"><div className="spinner" />Loading case...</div></div>;

  return (
    <div className="page case-review-page">
      <div className="page-title">
        <div>
          <div className="eyebrow">OPHTHALMOLOGIST CASE REVIEW</div>
          <h1>{caseId}</h1>
          <p className="muted">Review the complete screening record before recording a clinical decision.</p>
        </div>
        <div className={`badge large ${completed ? "success" : "warning"}`}>{screening.status || "-"}</div>
      </div>

      {error && <div className="auth-error">{error}</div>}

      <div className="case-review-grid">
        <Card title="Patient information">
          <div className="detail-grid">{[["Patient ID", patient.patient_id], ["Patient name", patient.name], ["Age", patient.age], ["Gender", patient.gender], ["Diabetes status", patient.diabetes_status], ["Diabetes duration", patient.diabetes_duration], ["Screening location", patient.screening_location], ["Screening date", formatDate(screening.created_at)]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || "-"}</strong></div>)}</div>
        </Card>
        <Card title="Screening information">
          <div className="detail-grid">{[["Screening ID", report?.screening_id], ["Evaluated eye", screening.evaluated_eye], ["Screening date/time", formatDate(screening.created_at)], ["AI DR grade", qualityRejected ? "Not performed" : ai.dr_grade ?? "-"], ["Severity", qualityRejected ? "Not available" : ai.severity_name], ["Confidence", qualityRejected ? "Not available" : ai.confidence_percent], ["Risk", qualityRejected ? "Not available" : ai.risk], ["Recommendation", qualityRejected ? "Recapture required" : ai.recommendation], ["Case status", screening.status]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || "-"}</strong></div>)}</div>
        </Card>
      </div>

      <ComparisonSection comparison={comparison} />

      <Card title="Image quality" subtitle="Quality metrics recorded by the screening pipeline">
        <div className="detail-grid quality-detail-grid">{metricRows.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value ?? "-"}</strong></div>)}</div>
        {qualityRejected && <div className="notice"><ShieldCheck size={18}/><div><strong>AI disease prediction was not performed.</strong><span>The image did not meet quality requirements. A new fundus image is required before screening can continue.</span></div></div>}
      </Card>

      <Card title="Visual AI evidence" subtitle="Stored evidence from the screening pipeline">
        <div className="evidence-grid">
          <EvidenceImage label="Original Fundus Image" src={originalImage} />
          <EvidenceImage label="Grad-CAM Explanation" src={gradcamImage} />
        </div>
        <p className="evidence-caption">Grad-CAM visualizes regions that contributed to the model prediction. It is an AI attention visualization and is not a direct lesion measurement.</p>
      </Card>

      <Card title="Lesion evidence">
        {lesionImage ? <EvidenceImage label="Lesion Evidence" src={lesionImage} /> : <p className="muted">Lesion-specific evidence is not available for this screening.</p>}
      </Card>

      <Card title={completed ? "Doctor review completed" : "Doctor review"} subtitle={completed ? `Reviewed by ${report.doctor_review.doctor_name || "Ophthalmologist"} on ${formatDate(report.doctor_review.reviewed_at)}` : "AI is decision support. The ophthalmologist remains responsible for the final clinical review."}>
        <div className="radio-list">
          {decisions.map(([value, label]) => (
            <label key={value} className={decision === value ? "radio selected" : "radio"}>
              <input type="radio" checked={decision === value} disabled={completed} onChange={() => setDecision(value)}/><span>{label}</span>
            </label>
          ))}
        </div>

        {decision === "MODIFY_GRADE" && <label>Final DR grade
          <select value={finalGrade} disabled={completed} onChange={e => setFinalGrade(e.target.value)}>
            <option value="">Use AI grade / not specified</option>
            <option value="0">0 — No DR</option>
            <option value="1">1 — Mild</option>
            <option value="2">2 — Moderate</option>
            <option value="3">3 — Severe</option>
            <option value="4">4 — Proliferative</option>
          </select>
        </label>}

        <label>Doctor notes
          <textarea rows="5" disabled={completed} value={notes} onChange={e => setNotes(e.target.value)} placeholder="Add relevant findings or follow-up instructions..."/>
        </label>
      </Card>

      <div className="form-actions">
        <Button variant="secondary" onClick={() => navigate("/dashboard")}><ArrowLeft size={17}/> Back to cases</Button>
        <Button variant="secondary" onClick={() => navigate(`/report/${caseId}`)}>View Screening Report</Button>
        <a className="btn btn-secondary" href={reportApi.pdfUrl(caseId)} target="_blank" rel="noreferrer"><Download size={17}/> Open Report PDF</a>
        {!completed && <Button onClick={submit} disabled={loading || qualityRejected}>{loading ? "Saving..." : <>Save review <FileCheck2 size={17}/></>}</Button>}
      </div>
    </div>
  );
}

function EvidenceImage({ label, src }) {
  return <div className="evidence-image"><div className="evidence-image-title"><ImageIcon size={15}/>{label}</div>{src ? <img src={toAbsoluteUrl(src)} alt={label} /> : <span className="muted">Stored image not available.</span>}</div>;
}

function ComparisonSection({ comparison }) {
  if (!comparison) return null;
  if (!comparison.previous) {
    return <Card title="Previous vs current screening" subtitle="Read-only historical comparison"><p className="muted">No previous screening available for comparison.</p></Card>;
  }

  const eyes = [...new Set([
    ...Object.keys(comparison.previous.eyes || {}),
    ...Object.keys(comparison.current.eyes || {}),
  ])].filter(eye => ["OD", "OS", "RIGHT", "LEFT"].includes(eye.toUpperCase()));

  return (
    <Card title="Previous vs current screening" subtitle="Read-only comparison of AI screening evidence">
      <div className="comparison-header">
        <div><span>Patient</span><strong>{comparison.patient.name || "-"} · {comparison.patient.patient_id}</strong></div>
        <div><span>Current screening date</span><strong>{formatDate(comparison.current.created_at)}</strong></div>
        <div><span>Previous screening date</span><strong>{formatDate(comparison.previous.created_at)}</strong></div>
      </div>
      <div className="comparison-eyes">
        {eyes.length ? eyes.map(eye => <EyeComparison key={eye} eye={eye} previous={comparison.previous.eyes[eye]} current={comparison.current.eyes[eye]} />) : <p className="muted">No eye-specific screening data available for comparison.</p>}
      </div>
      <p className="comparison-disclaimer">AI screening results are provided for decision support. Changes in AI-assigned grade do not by themselves establish disease progression. Final interpretation is by the ophthalmologist.</p>
    </Card>
  );
}

function EyeComparison({ eye, previous, current }) {
  const previousAi = previous?.ai_prediction || {};
  const currentAi = current?.ai_prediction || {};
  const previousGrade = numericGrade(previousAi.dr_grade);
  const currentGrade = numericGrade(currentAi.dr_grade);
  const change = gradeChange(previousGrade, currentGrade);

  return (
    <section className="eye-comparison">
      <div className="eye-comparison-title"><strong>{eyeLabel(eye)}</strong><span>Change in AI-assigned screening grade: {change}</span></div>
      <div className="comparison-cards">
        <ComparisonCard title="PREVIOUS SCREENING" date={previous?.created_at} image={previous?.image?.file_url} gradcam={previousAi.gradcam_url || previousAi.gradcam_urls?.overlay} grade={previousGrade} confidence={previousAi.confidence_percent} quality={qualityStatus(previous?.quality)} missingEvidence="Previous Grad-CAM unavailable." />
        <ComparisonCard title="CURRENT SCREENING" date={current?.created_at} image={current?.image?.file_url} gradcam={currentAi.gradcam_url || currentAi.gradcam_urls?.overlay} grade={currentGrade} confidence={currentAi.confidence_percent} quality={qualityStatus(current?.quality)} missingEvidence="Current Grad-CAM unavailable." />
      </div>
      <div className="comparison-summary"><div><span>Previous grade</span><strong>{displayGrade(previousGrade)}</strong></div><div><span>Current grade</span><strong>{displayGrade(currentGrade)}</strong></div><div><span>AI grade change</span><strong>{change}</strong></div><div><span>Previous confidence</span><strong>{previousAi.confidence_percent || "-"}</strong></div><div><span>Current confidence</span><strong>{currentAi.confidence_percent || "-"}</strong></div><div><span>Quality status</span><strong>{qualityStatus(current?.quality)}</strong></div></div>
    </section>
  );
}

function ComparisonCard({ title, date, image, gradcam, grade, confidence, quality, missingEvidence }) {
  return <div className="comparison-card"><h3>{title}</h3><EvidenceImage label="Fundus image" src={image} /><div className="comparison-meta"><div><span>Date</span><strong>{formatDate(date)}</strong></div><div><span>Grade</span><strong>{displayGrade(grade)}</strong></div><div><span>Confidence</span><strong>{confidence || "-"}</strong></div><div><span>Quality</span><strong>{quality}</strong></div></div><div className="comparison-gradcam">{gradcam ? <><span>Grad-CAM</span><img src={toAbsoluteUrl(gradcam)} alt={`${title} Grad-CAM`} /></> : <span>{missingEvidence}</span>}</div></div>;
}

function numericGrade(value) {
  return value === null || value === undefined || value === "" || Number.isNaN(Number(value)) ? null : Number(value);
}

function displayGrade(value) {
  return value === null ? "Unavailable" : `Grade ${value}`;
}

function gradeChange(previous, current) {
  if (previous === null || current === null) return "Unavailable";
  if (current === previous) return "Same";
  return current > previous ? "Higher grade" : "Lower grade";
}

function qualityStatus(quality) {
  return quality?.final_status || quality?.overall_status || "Unavailable";
}

function eyeLabel(eye) {
  return eye === "OD" || eye === "RIGHT" ? "RIGHT EYE" : eye === "OS" || eye === "LEFT" ? "LEFT EYE" : eye;
}

const formatDate = (value) => {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleString();
};
