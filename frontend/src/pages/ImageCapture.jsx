
import { useRef, useState } from "react";
import { UploadCloud, ArrowLeft, ArrowRight, CheckCircle2, Image as ImageIcon } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { screeningApi } from "../services/api";

export default function ImageCapture() {
  const { patientId: caseId } = useParams();
  const navigate = useNavigate();

  const rightInput = useRef();
  const leftInput = useRef();

  const [files, setFiles] = useState({ OD: null, OS: null });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const choose = (eye, file) => {
    setFiles(prev => ({ ...prev, [eye]: file || null }));
  };

  const upload = async () => {
    if (!files.OD && !files.OS) return;

    setError("");
    setLoading(true);

    try {
      if (files.OD) await screeningApi.upload(caseId, "OD", files.OD);
      if (files.OS) await screeningApi.upload(caseId, "OS", files.OS);
      navigate(`/quality/${caseId}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Image upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page narrow-page">
      <div className="page-title">
        <div>
          <div className="eyebrow">STEP 2 OF 5 · {caseId}</div>
          <h1>Upload retinal images</h1>
          <p className="muted">Image upload only. Camera capture is intentionally disabled for this prototype.</p>
        </div>
      </div>

      <div className="stepper"><span className="done">✓</span><i/><span className="done">2</span><i/><span>3</span><i/><span>4</span><i/><span>5</span></div>

      <Card title="Fundus image upload" subtitle="Accepted: JPG, JPEG, PNG · Maximum 10 MB per image">
        {error && <div className="auth-error">{error}</div>}

        <div className="form-grid">
          {[
            ["OD", "Right eye", rightInput],
            ["OS", "Left eye", leftInput],
          ].map(([eye, label, ref]) => (
            <div className="card" key={eye}>
              <div className="card-head">
                <div><h3>{label}</h3><p>{eye}</p></div>
              </div>

              <input
                ref={ref}
                type="file"
                accept="image/jpeg,image/png"
                hidden
                onChange={e => choose(eye, e.target.files?.[0])}
              />

              <div className="dropzone" onClick={() => ref.current?.click()}>
                <UploadCloud size={35}/>
                <h3>{files[eye] ? "Image selected" : "Choose fundus image"}</h3>
                <p>{files[eye]?.name || "Click to browse your device"}</p>
                <Button type="button" variant="secondary">Browse</Button>
              </div>

              {files[eye] && (
                <div className="file-item">
                  <ImageIcon size={20}/>
                  <div>
                    <strong>{files[eye].name}</strong>
                    <span>{(files[eye].size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  <CheckCircle2 className="file-ok"/>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="form-actions">
          <Button variant="secondary" onClick={() => navigate("/patients/new")}>
            <ArrowLeft size={17}/> Back
          </Button>
          <Button onClick={upload} disabled={(!files.OD && !files.OS) || loading}>
            {loading ? "Uploading..." : <>Continue to quality check <ArrowRight size={17}/></>}
          </Button>
        </div>
      </Card>
    </div>
  );
}
