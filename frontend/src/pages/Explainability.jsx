
import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Info, Image as ImageIcon } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../components/Button";
import Card from "../components/Card";
import { screeningApi, toAbsoluteUrl } from "../services/api";

export default function Explainability() {
  const { patientId: caseId } = useParams();
  const navigate = useNavigate();
  const [screening, setScreening] = useState(null);

  useEffect(() => {
    screeningApi.get(caseId).then(({data}) => setScreening(data));
  }, [caseId]);

  const ai = screening?.ai_prediction;
  const image = screening?.images?.[ai?.eye] || screening?.images?.OD || screening?.images?.OS;
  const gradcam = ai?.gradcam_urls || {};

  return (
    <div className="page">
      <div className="page-title">
        <div>
          <div className="eyebrow">STEP 4 OF 5 · EXPLAINABILITY</div>
          <h1>Why did the model predict this?</h1>
          <p className="muted">Case <strong>{caseId}</strong></p>
        </div>
      </div>

      <div className="explain-grid">
        <Card title="Original processed image" subtitle={ai?.eye || "Fundus image"}>
          <div className="explain-image">
            {gradcam.original ? <img src={toAbsoluteUrl(gradcam.original)} alt="Processed fundus" style={{width:"100%",height:"100%",objectFit:"contain"}}/> : image ? <img src={toAbsoluteUrl(image.file_url)} alt="Fundus" style={{width:"100%",height:"100%",objectFit:"contain"}}/> : <ImageIcon size={42}/>}
          </div>
        </Card>

        <Card title="AI attention map" subtitle={ai?.gradcam_url ? "Grad-CAM" : "Waiting for DL model"}>
          <div className="explain-image heat">
            {gradcam.heatmap || ai?.gradcam_url ? (
              <img src={toAbsoluteUrl(gradcam.heatmap || ai.gradcam_url)} alt="Grad-CAM heatmap" style={{width:"100%",height:"100%",objectFit:"contain"}}/>
            ) : (
              <div className="muted" style={{color:"#fff"}}>Grad-CAM is unavailable.</div>
            )}
          </div>
        </Card>
      </div>

      <div className="explain-bottom">
        <Card title="Model evidence">
          {ai?.lesion_evidence_url && <img src={toAbsoluteUrl(ai.lesion_evidence_url)} alt="AI-generated lesion evidence" style={{width:"100%",maxHeight:320,objectFit:"contain"}}/>}
          {ai?.lesions?.length ? (
            ai.lesions.map((item, i) => <div className="evidence" key={i}><div><span>{typeof item === "string" ? item : item.name}</span><strong>Evidence</strong></div></div>)
          ) : (
            <p className="muted">No AI-generated lesion evidence was returned.</p>
          )}
          <p className="muted">AI-generated lesion evidence - research/demo; not clinically confirmed.</p>
        </Card>

        <Card title="How to interpret" className="info-card">
          <Info/>
          <p>Highlighted regions should be interpreted as model evidence, not proof of disease. Final clinical determination remains with a qualified clinician.</p>
        </Card>
      </div>

      <div className="form-actions">
        <Button variant="secondary" onClick={() => navigate(`/screening/${caseId}`)}><ArrowLeft size={17}/> Back</Button>
        <Button onClick={() => navigate(`/doctor-review/${caseId}`)}>Doctor review <ArrowRight size={17}/></Button>
      </div>
    </div>
  );
}
