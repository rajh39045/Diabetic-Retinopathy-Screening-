
import { useState } from "react";
import { ArrowLeft, ArrowRight, UserRound } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { patientApi, screeningApi } from "../services/api";

function calculateAge(dob) {
  const birth = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age;
}

export default function PatientRegistration() {
  const [form, setForm] = useState({
    patientId: "",
    name: "",
    dob: "",
    gender: "",
    phone: "",
    diabetesStatus: "",
    diabetesDuration: "",
    screeningLocation: "",
    consent: true,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    const patientId = form.patientId.trim() ||
      `PT-${Date.now().toString().slice(-6)}`;

    const age = calculateAge(form.dob);
    if (age < 0 || age > 120) {
      setError("Please enter a valid date of birth.");
      return;
    }

    setLoading(true);

    try {
      await patientApi.create({
        patient_id: patientId,
        name: form.name.trim(),
        age,
        gender: form.gender,
        phone: form.phone || null,
        diabetes_status: form.diabetesStatus,
        diabetes_duration: form.diabetesDuration || null,
        screening_location: form.screeningLocation,
      });

      const caseId = `CASE-${Date.now()}`;

      await screeningApi.create({
        case_id: caseId,
        patient_id: patientId,
        screening_location: form.screeningLocation,
        evaluated_eye: "BOTH",
      });

      navigate(`/capture/${caseId}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create screening.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page narrow-page">
      <div className="page-title">
        <div>
          <div className="eyebrow">STEP 1 OF 5</div>
          <h1>Register patient</h1>
          <p className="muted">Patient and screening data will be stored in MongoDB.</p>
        </div>
      </div>

      <div className="stepper"><span className="done">1</span><i/><span>2</span><i/><span>3</span><i/><span>4</span><i/><span>5</span></div>

      <Card title="Patient details" subtitle="Only the data required for screening is collected.">
        <form className="form-grid" onSubmit={submit}>
          {error && <div className="full-col auth-error">{error}</div>}

          <label className="full-col">Patient ID
            <input value={form.patientId} onChange={e => set("patientId", e.target.value)} placeholder="Optional — auto-generated if empty"/>
          </label>

          <label>Full name
            <input value={form.name} onChange={e => set("name", e.target.value)} required/>
          </label>

          <label>Date of birth
            <input type="date" value={form.dob} onChange={e => set("dob", e.target.value)} required/>
          </label>

          <label>Gender
            <select value={form.gender} onChange={e => set("gender", e.target.value)} required>
              <option value="">Select</option>
              <option>Female</option><option>Male</option><option>Other</option>
            </select>
          </label>

          <label>Phone number
            <input value={form.phone} onChange={e => set("phone", e.target.value)} placeholder="+91..."/>
          </label>

          <label>Diabetes status
            <select value={form.diabetesStatus} onChange={e => set("diabetesStatus", e.target.value)} required>
              <option value="">Select</option>
              <option>Diabetic</option>
              <option>Non-diabetic</option>
              <option>Unknown</option>
            </select>
          </label>

          <label>Diabetes duration
            <input value={form.diabetesDuration} onChange={e => set("diabetesDuration", e.target.value)} placeholder="e.g. 6 years"/>
          </label>

          <label className="full-col">Screening location
            <input value={form.screeningLocation} onChange={e => set("screeningLocation", e.target.value)} required placeholder="Primary health centre / camp"/>
          </label>

          <label className="full-col check consent">
            <input type="checkbox" checked={form.consent} onChange={e => set("consent", e.target.checked)}/>
            Patient consent for retinal screening and AI-assisted assessment has been obtained.
          </label>

          <div className="form-actions full-col">
            <Button type="button" variant="secondary" onClick={() => navigate("/dashboard")}>
              <ArrowLeft size={17}/> Cancel
            </Button>
            <Button disabled={!form.consent || loading}>
              {loading ? "Creating..." : <>Continue to image upload <ArrowRight size={17}/></>}
            </Button>
          </div>
        </form>
      </Card>

      <div className="info-banner">
        <UserRound size={19}/>
        <div><strong>Clinical note</strong><span>AI output is decision support and should be reviewed by a qualified clinician.</span></div>
      </div>
    </div>
  );
}
