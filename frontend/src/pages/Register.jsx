
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/Button";
import { authApi } from "../services/api";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "HEALTHCARE_WORKER",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authApi.register(form);
      navigate("/login", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-simple">
      <form className="auth-card" onSubmit={submit}>
        <div className="brand-center">RETINA-XAI</div>
        <div className="eyebrow">ACCOUNT SETUP</div>
        <h2>Create your clinical account</h2>
        <p className="muted">Your account is stored in the RETINA-XAI backend database.</p>

        {error && <div className="auth-error">{error}</div>}

        <label>Full name
          <input value={form.name} onChange={e => update("name", e.target.value)} required />
        </label>

        <label>Work email
          <input type="email" value={form.email} onChange={e => update("email", e.target.value)} required />
        </label>

        <label>Role
          <select value={form.role} onChange={e => update("role", e.target.value)}>
            <option value="HEALTHCARE_WORKER">Healthcare Worker</option>
            <option value="OPHTHALMOLOGIST">Ophthalmologist</option>
          </select>
        </label>

        <label>Password
          <input type="password" minLength={8} value={form.password} onChange={e => update("password", e.target.value)} required />
        </label>

        <Button className="full" disabled={loading}>
          {loading ? "Creating..." : "Create account"}
        </Button>

        <p className="auth-bottom">Already registered? <Link to="/login">Sign in</Link></p>
      </form>
    </div>
  );
}
