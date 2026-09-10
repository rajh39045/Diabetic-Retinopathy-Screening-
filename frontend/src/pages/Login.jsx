
import { useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { ShieldCheck, Stethoscope } from "lucide-react";

import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await authApi.login({ email, password });
      login(data);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-visual">
        <div className="auth-logo"><Stethoscope size={24}/> RETINA-XAI</div>
        <div className="auth-hero">
          <div className="retina-art">
            <div className="retina-core"/>
            <div className="vessel v1"/>
            <div className="vessel v2"/>
            <div className="vessel v3"/>
          </div>
          <h1>See the retina.<br/><em>Understand the AI.</em></h1>
          <p>Clinical screening with transparent, explainable intelligence designed for confident decisions.</p>
        </div>
        <div className="auth-trust"><ShieldCheck size={18}/> Secure clinical workspace</div>
      </div>

      <div className="auth-form-area">
        <form className="auth-card" onSubmit={submit}>
          <div className="mobile-brand">RETINA-XAI</div>
          <div className="eyebrow">WELCOME BACK</div>
          <h2>Sign in to your workspace</h2>
          <p className="muted">Use your RETINA-XAI account.</p>

          {error && <div className="auth-error">{error}</div>}

          <label>Email address
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </label>

          <label>Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </label>

          <Button type="submit" className="full" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>

          <p className="auth-bottom">
            Don't have an account? <Link to="/register">Create one</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
