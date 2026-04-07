import { useState } from "react";
import { apiFetch } from "../utils/Helpers.js";

// ─── AUTH PAGE ────────────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
function AuthPage({ onAuth }) {
  const [tab, setTab] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const submit = async () => {
    setErr(""); setLoading(true);
    try {
      if (tab === "register") {
        await apiFetch("/auth/register", null, {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        setTab("login");
        setErr("");
        return;
      }
      const data = await apiFetch("/auth/login", null, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      onAuth(data.access_token, email);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-box">
        <div className="auth-title">MSRP</div>
        <div className="auth-sub">Market Signal & Research Platform</div>
        <div className="auth-tabs">
          {["login", "register"].map(t => (
            <button key={t} className={`auth-tab${tab === t ? " active" : ""}`} onClick={() => { setTab(t); setErr(""); }}>
              {t === "login" ? "Sign In" : "Register"}
            </button>
          ))}
        </div>
        <div className="field">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="analyst@firm.com" />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === "Enter" && submit()} placeholder="••••••••" />
        </div>
        <button className="btn btn-primary" onClick={submit} disabled={loading || !email || !password}>
          {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Loading…</> : (tab === "login" ? "Sign In" : "Create Account")}
        </button>
        {err && <div className="err">⚠ {err}</div>}
        {tab === "register" && !err && (
          <div style={{ marginTop: 12, fontSize: 11, color: "var(--muted)" }}>
            After registering, sign in to access the platform.
          </div>
        )}
      </div>
    </div>
  );
}

// Change added
export { AuthPage };