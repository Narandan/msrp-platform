import { useState, useEffect, useRef, useCallback } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, ComposedChart
} from "recharts";

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API = "http://127.0.0.1:8000";

// ─── STYLES ──────────────────────────────────────────────────────────────────
const STYLE = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #09090b;
    --surface:  #111114;
    --border:   #1e1e24;
    --border2:  #2a2a34;
    --text:     #e8e8f0;
    --muted:    #6b6b80;
    --accent:   #c8f542;
    --accent2:  #42d4f5;
    --red:      #f55142;
    --green:    #42f5a1;
    --orange:   #f5a142;
    --font-body: 'DM Mono', monospace;
    --font-head: 'Syne', sans-serif;
    --radius:   6px;
  }

  html, body, #root { height: 100%; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 13px;
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

  /* layout */
  .app { display: flex; flex-direction: column; min-height: 100vh; }

  /* ── topbar ── */
  .topbar {
    display: flex; align-items: center; gap: 24px;
    padding: 0 28px; height: 56px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky; top: 0; z-index: 100;
  }
  .logo {
    font-family: var(--font-head);
    font-size: 18px; font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--accent);
  }
  .logo span { color: var(--text); }
  .topbar-nav { display: flex; gap: 2px; margin-left: 16px; }
  .nav-btn {
    background: none; border: none; cursor: pointer;
    padding: 6px 14px; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px;
    color: var(--muted); letter-spacing: 0.04em;
    transition: all 0.15s;
  }
  .nav-btn:hover { color: var(--text); background: var(--border); }
  .nav-btn.active { color: var(--accent); background: rgba(200,245,66,0.08); }
  .topbar-right { margin-left: auto; display: flex; align-items: center; gap: 12px; }
  .user-pill {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 12px; background: var(--border); border-radius: 20px;
    font-size: 11px; color: var(--muted);
  }
  .user-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }

  /* ── auth ── */
  .auth-wrap {
    flex: 1; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(ellipse at 50% 0%, rgba(200,245,66,0.04) 0%, transparent 60%);
  }
  .auth-box {
    width: 380px; padding: 40px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    animation: fadeUp 0.4s ease;
  }
  .auth-title {
    font-family: var(--font-head); font-size: 26px; font-weight: 800;
    margin-bottom: 4px;
  }
  .auth-sub { color: var(--muted); font-size: 12px; margin-bottom: 28px; }
  .auth-tabs { display: flex; gap: 4px; margin-bottom: 28px; }
  .auth-tab {
    flex: 1; padding: 8px; border: 1px solid var(--border2);
    background: none; cursor: pointer; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px; color: var(--muted);
    transition: all 0.15s;
  }
  .auth-tab.active { border-color: var(--accent); color: var(--accent); background: rgba(200,245,66,0.06); }

  /* ── form ── */
  .field { margin-bottom: 16px; }
  .field label { display: block; font-size: 11px; color: var(--muted); margin-bottom: 6px; letter-spacing: 0.06em; text-transform: uppercase; }
  .field input, .field select {
    width: 100%; padding: 10px 12px;
    background: var(--bg); border: 1px solid var(--border2);
    border-radius: var(--radius); color: var(--text);
    font-family: var(--font-body); font-size: 13px;
    outline: none; transition: border 0.15s;
    appearance: none;
  }
  .field input:focus, .field select:focus { border-color: var(--accent); }
  .btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    padding: 10px 20px; border: none; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 13px; cursor: pointer;
    transition: all 0.15s; font-weight: 500;
  }
  .btn-primary {
    background: var(--accent); color: var(--bg);
    width: 100%;
  }
  .btn-primary:hover { opacity: 0.88; }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-ghost {
    background: var(--border); color: var(--text);
  }
  .btn-ghost:hover { background: var(--border2); }
  .btn-danger {
    background: rgba(245,81,66,0.12); color: var(--red); border: 1px solid rgba(245,81,66,0.3);
  }
  .btn-danger:hover { background: rgba(245,81,66,0.2); }
  .err { color: var(--red); font-size: 12px; margin-top: 12px; }

  /* ── main content ── */
  .main { flex: 1; display: flex; }
  .sidebar {
    width: 240px; min-height: 0;
    border-right: 1px solid var(--border);
    background: var(--surface);
    display: flex; flex-direction: column;
    padding: 20px 0;
    position: sticky; top: 56px; height: calc(100vh - 56px);
    overflow-y: auto;
  }
  .sidebar-section { padding: 0 16px; margin-bottom: 24px; }
  .sidebar-label {
    font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 8px; padding: 0 4px;
  }
  .sidebar-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: var(--radius);
    cursor: pointer; transition: all 0.12s;
    font-size: 12px; color: var(--muted);
    border: 1px solid transparent;
  }
  .sidebar-item:hover { background: var(--border); color: var(--text); }
  .sidebar-item.active {
    background: rgba(200,245,66,0.07);
    border-color: rgba(200,245,66,0.2);
    color: var(--accent);
  }
  .sidebar-icon { font-size: 14px; width: 18px; text-align: center; }
  .content { flex: 1; padding: 28px; overflow-y: auto; }

  /* ── page titles ── */
  .page-header { margin-bottom: 28px; }
  .page-title {
    font-family: var(--font-head); font-size: 24px; font-weight: 800;
    margin-bottom: 4px;
  }
  .page-sub { color: var(--muted); font-size: 12px; }

  /* ── cards ── */
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 24px;
    animation: fadeUp 0.3s ease;
  }
  .card-title {
    font-family: var(--font-head); font-size: 14px; font-weight: 700;
    margin-bottom: 18px; color: var(--text);
    display: flex; align-items: center; gap: 8px;
  }
  .card-title .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent);
  }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }

  /* ── stat chips ── */
  .stat-chip {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px;
  }
  .stat-chip-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
  .stat-chip-val { font-size: 22px; font-family: var(--font-head); font-weight: 700; }
  .stat-chip-val.pos { color: var(--green); }
  .stat-chip-val.neg { color: var(--red); }
  .stat-chip-val.neu { color: var(--accent2); }

  /* ── symbol search ── */
  .search-row { display: flex; gap: 8px; align-items: flex-end; flex-wrap: wrap; }
  .search-row .field { margin: 0; flex: 1; min-width: 120px; }
  .autocomplete-wrap { position: relative; flex: 1; min-width: 120px; }
  .autocomplete-list {
    position: absolute; top: calc(100% + 4px); left: 0; right: 0;
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: var(--radius); z-index: 50;
    max-height: 180px; overflow-y: auto;
  }
  .autocomplete-item {
    padding: 8px 12px; cursor: pointer; font-size: 12px;
    display: flex; align-items: center; gap: 8px;
    transition: background 0.1s;
  }
  .autocomplete-item:hover { background: var(--border); }
  .autocomplete-ticker { color: var(--accent); font-weight: 500; }
  .autocomplete-name { color: var(--muted); }

  /* ── table ── */
  .tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
  .tbl th {
    text-align: left; padding: 8px 12px;
    font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); border-bottom: 1px solid var(--border);
    font-weight: 500;
  }
  .tbl td { padding: 9px 12px; border-bottom: 1px solid var(--border); }
  .tbl tr:last-child td { border-bottom: none; }
  .tbl tr:hover td { background: rgba(255,255,255,0.02); }
  .pos { color: var(--green); }
  .neg { color: var(--red); }
  .muted { color: var(--muted); }

  /* ── badge ── */
  .badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 4px; font-size: 10px; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
  }
  .badge-buy { background: rgba(66,245,161,0.12); color: var(--green); }
  .badge-sell { background: rgba(245,81,66,0.12); color: var(--red); }
  .badge-hold { background: rgba(107,107,128,0.2); color: var(--muted); }

  /* ── tooltip ── */
  .chart-tooltip {
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: var(--radius); padding: 10px 14px;
    font-size: 11px;
  }
  .chart-tooltip .label { color: var(--muted); margin-bottom: 4px; }

  /* ── tabs ── */
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }
  .tab-btn {
    background: none; border: 1px solid transparent; cursor: pointer;
    padding: 6px 14px; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px; color: var(--muted);
    transition: all 0.15s;
  }
  .tab-btn:hover { color: var(--text); border-color: var(--border2); }
  .tab-btn.active { color: var(--accent); border-color: rgba(200,245,66,0.3); background: rgba(200,245,66,0.06); }

  /* ── spinner ── */
  .spinner {
    width: 20px; height: 20px; border-radius: 50%;
    border: 2px solid var(--border2); border-top-color: var(--accent);
    animation: spin 0.6s linear infinite;
  }
  .loading-row { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 40px; color: var(--muted); font-size: 12px; }

  /* ── empty ── */
  .empty { text-align: center; padding: 48px 24px; color: var(--muted); }
  .empty-icon { font-size: 32px; margin-bottom: 12px; }
  .empty-text { font-size: 13px; }

  /* ── separator ── */
  .sep { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

  /* ── ingest panel ── */
  .ingest-result {
    display: flex; gap: 12px; padding: 14px;
    background: rgba(200,245,66,0.05); border: 1px solid rgba(200,245,66,0.2);
    border-radius: var(--radius); margin-top: 16px;
    font-size: 12px;
  }
  .ingest-result span { color: var(--muted); }
  .ingest-result strong { color: var(--accent); }

  /* ── animations ── */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── indicator toggle pills ── */
  .pill-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
  .pill {
    padding: 4px 12px; border-radius: 20px; font-size: 11px;
    border: 1px solid var(--border2); cursor: pointer;
    transition: all 0.12s; color: var(--muted); background: none;
    font-family: var(--font-body);
  }
  .pill.on { border-color: var(--accent2); color: var(--accent2); background: rgba(66,212,245,0.08); }
  .pill.sma { border-color: var(--orange); color: var(--orange); background: rgba(245,161,66,0.08); }
  .pill.ema { border-color: #b066f5; color: #b066f5; background: rgba(176,102,245,0.08); }
  .pill.rsi { border-color: var(--accent2); color: var(--accent2); background: rgba(66,212,245,0.08); }
  .pill.bb  { border-color: var(--green); color: var(--green); background: rgba(66,245,161,0.08); }

  /* responsive */
  @media (max-width: 900px) {
    .sidebar { display: none; }
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  }
`;

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const fmt = (n, d = 2) =>
  n == null ? "—" : Number(n).toFixed(d);

const fmtPct = (n) =>
  n == null ? "—" : `${n > 0 ? "+" : ""}${Number(n).toFixed(2)}%`;

const fmtDate = (d) => d ? String(d).slice(0, 10) : "—";

async function apiFetch(path, token, opts = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { headers, ...opts });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const msg = Array.isArray(detail)
      ? detail.map(e => e.msg).join(", ")
      : (typeof detail === "string" ? detail : `HTTP ${res.status}`);
    throw new Error(msg);
  }
  return res.json();
}

// ─── CUSTOM TOOLTIP ──────────────────────────────────────────────────────────
function ChartTip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, display: "flex", gap: 8, justifyContent: "space-between" }}>
          <span>{p.name}</span>
          <span style={{ fontWeight: 600 }}>{fmt(p.value, 4)}</span>
        </div>
      ))}
    </div>
  );
}

// ─── AUTH PAGE ────────────────────────────────────────────────────────────────
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

// ─── INGEST PAGE ──────────────────────────────────────────────────────────────
function IngestPage({ token }) {
  const [symbol, setSymbol] = useState("");
  const [start, setStart] = useState("2024-01-01");
  const [end, setEnd] = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  const run = async () => {
    setErr(""); setResult(null); setLoading(true);
    try {
      const data = await apiFetch(`/stocks/${symbol.toUpperCase()}/ingest?start=${start}&end=${end}`, token, { method: "POST" });
      setResult(data);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Data Ingest</div>
        <div className="page-sub">Fetch and store OHLCV candles from Stooq for any ticker</div>
      </div>
      <div className="card" style={{ maxWidth: 540 }}>
        <div className="card-title"><span className="dot" />Ingest Symbol</div>
        <div className="field">
          <label>Ticker Symbol</label>
          <input value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} placeholder="AAPL" />
        </div>
        <div className="grid-2">
          <div className="field"><label>Start Date</label><input type="date" value={start} onChange={e => setStart(e.target.value)} /></div>
          <div className="field"><label>End Date</label><input type="date" value={end} onChange={e => setEnd(e.target.value)} /></div>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading || !symbol}>
          {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Ingesting…</> : "↓ Ingest Data"}
        </button>
        {err && <div className="err">⚠ {err}</div>}
        {result && (
          <div className="ingest-result">
            <div>Inserted <strong>{result.inserted}</strong></div>
            <div>Skipped <strong style={{ color: "var(--muted)" }}>{result.skipped}</strong></div>
            <div>Total seen <strong>{result.total_seen}</strong></div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── CANDLES PAGE ─────────────────────────────────────────────────────────────
function CandlesPage({ token }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [limit, setLimit] = useState(200);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSug, setShowSug] = useState(false);

  const fetchSuggestions = async (q) => {
    if (!q || q.length < 1) { setSuggestions([]); return; }
    try {
      const res = await apiFetch(`/stocks/search?q=${q}&limit=8`, token);
      setSuggestions(res);
    } catch { setSuggestions([]); }
  };

  const load = async () => {
    setErr(""); setLoading(true);
    try {
      const d = await apiFetch(`/stocks/${symbol.toUpperCase()}/candles?limit=${limit}`, token);
      setData(d);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Price Chart</div>
        <div className="page-sub">OHLCV candle data for any ingested symbol</div>
      </div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="search-row">
          <div className="autocomplete-wrap">
            <div className="field" style={{ margin: 0 }}>
              <label>Symbol</label>
              <input
                value={symbol}
                onChange={e => { setSymbol(e.target.value.toUpperCase()); fetchSuggestions(e.target.value); setShowSug(true); }}
                onFocus={() => setShowSug(true)}
                onBlur={() => setTimeout(() => setShowSug(false), 150)}
                placeholder="AAPL"
              />
            </div>
            {showSug && suggestions.length > 0 && (
              <div className="autocomplete-list">
                {suggestions.map(s => (
                  <div key={s.ticker} className="autocomplete-item" onMouseDown={() => { setSymbol(s.ticker); setSuggestions([]); }}>
                    <span className="autocomplete-ticker">{s.ticker}</span>
                    {s.name && <span className="autocomplete-name">{s.name}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="field" style={{ margin: 0, maxWidth: 120 }}>
            <label>Max Candles</label>
            <input type="number" value={limit} onChange={e => setLimit(Number(e.target.value))} min={1} max={5000} />
          </div>
          <button className="btn btn-ghost" onClick={load} disabled={loading || !symbol} style={{ marginBottom: 0, alignSelf: "flex-end" }}>
            {loading ? "Loading…" : "Load →"}
          </button>
        </div>
        {err && <div className="err" style={{ marginTop: 8 }}>⚠ {err}</div>}
      </div>

      {data.length > 0 && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" style={{ background: "var(--accent2)" }} />{symbol} — Close Price</div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={data} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#42d4f5" stopOpacity={0.18} />
                    <stop offset="95%" stopColor="#42d4f5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
                <Tooltip content={<ChartTip />} />
                <Area type="monotone" dataKey="close" stroke="#42d4f5" fill="url(#cg)" strokeWidth={1.5} dot={false} name="Close" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" style={{ background: "var(--muted)" }} />Volume</div>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={data} margin={{ top: 0, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTip />} />
                <Bar dataKey="volume" fill="#2a2a34" name="Volume" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-title"><span className="dot" />Raw Candles</div>
            <div style={{ overflowX: "auto" }}>
              <table className="tbl">
                <thead>
                  <tr>
                    {["Date", "Open", "High", "Low", "Close", "Volume"].map(h => <th key={h}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {[...data].reverse().slice(0, 50).map((r, i) => (
                    <tr key={i}>
                      <td className="muted">{fmtDate(r.date)}</td>
                      <td>{fmt(r.open)}</td>
                      <td className="pos">{fmt(r.high)}</td>
                      <td className="neg">{fmt(r.low)}</td>
                      <td style={{ color: "var(--accent2)" }}>{fmt(r.close)}</td>
                      <td className="muted">{r.volume?.toLocaleString() ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.length > 50 && <div style={{ textAlign: "center", padding: "12px 0 0", color: "var(--muted)", fontSize: 11 }}>Showing latest 50 of {data.length} candles</div>}
          </div>
        </>
      )}

      {!loading && data.length === 0 && (
        <div className="empty"><div className="empty-icon">📊</div><div className="empty-text">Enter a symbol and click Load to view candle data</div></div>
      )}
    </div>
  );
}

// ─── INDICATORS PAGE ──────────────────────────────────────────────────────────
function IndicatorsPage({ token }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [start, setStart] = useState("2024-01-01");
  const [end, setEnd] = useState(new Date().toISOString().slice(0, 10));
  const [smaPeriod, setSmaPeriod] = useState(20);
  const [emaPeriod, setEmaPeriod] = useState(20);
  const [rsiPeriod, setRsiPeriod] = useState(14);
  const [bbPeriod, setBbPeriod] = useState(20);
  const [showSma, setShowSma] = useState(true);
  const [showEma, setShowEma] = useState(false);
  const [showBb, setShowBb] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const load = async () => {
    setErr(""); setLoading(true);
    try {
      let url = `/indicators/${symbol.toUpperCase()}?start=${start}&end=${end}`;
      if (showSma) url += `&sma_period=${smaPeriod}`;
      if (showEma) url += `&ema_period=${emaPeriod}`;
      url += `&rsi_period=${rsiPeriod}`;
      if (showBb) url += `&bb_period=${bbPeriod}`;
      const d = await apiFetch(url, token);
      setData(d);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  const pts = data?.points ?? [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Indicators</div>
        <div className="page-sub">SMA, EMA, RSI, Bollinger Bands for any symbol</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="grid-2" style={{ marginBottom: 12 }}>
          <div className="field"><label>Symbol</label><input value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} /></div>
          <div style={{ display: "flex", gap: 8 }}>
            <div className="field" style={{ flex: 1 }}><label>Start</label><input type="date" value={start} onChange={e => setStart(e.target.value)} /></div>
            <div className="field" style={{ flex: 1 }}><label>End</label><input type="date" value={end} onChange={e => setEnd(e.target.value)} /></div>
          </div>
        </div>

        <div className="pill-row">
          <button className={`pill sma${showSma ? " on" : ""}`} onClick={() => setShowSma(!showSma)}>
            SMA {showSma && `(${smaPeriod})`}
          </button>
          <button className={`pill ema${showEma ? " on" : ""}`} onClick={() => setShowEma(!showEma)}>
            EMA {showEma && `(${emaPeriod})`}
          </button>
          <button className={`pill bb${showBb ? " on" : ""}`} onClick={() => setShowBb(!showBb)}>
            Bollinger {showBb && `(${bbPeriod})`}
          </button>
        </div>

        {(showSma || showEma || showBb) && (
          <div className="grid-3" style={{ marginBottom: 12 }}>
            {showSma && <div className="field"><label>SMA Period</label><input type="number" value={smaPeriod} onChange={e => setSmaPeriod(Number(e.target.value))} min={1} /></div>}
            {showEma && <div className="field"><label>EMA Period</label><input type="number" value={emaPeriod} onChange={e => setEmaPeriod(Number(e.target.value))} min={1} /></div>}
            {showBb && <div className="field"><label>BB Period</label><input type="number" value={bbPeriod} onChange={e => setBbPeriod(Number(e.target.value))} min={1} /></div>}
          </div>
        )}

        <button className="btn btn-primary" onClick={load} disabled={loading || !symbol}>
          {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Loading…</> : "Calculate →"}
        </button>
        {err && <div className="err" style={{ marginTop: 8 }}>⚠ {err}</div>}
      </div>

      {pts.length > 0 && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" />{data.symbol} — Price + Overlays</div>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={pts} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
                <Tooltip content={<ChartTip />} />
                <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
                <Area type="monotone" dataKey="close" stroke="#42d4f5" fill="rgba(66,212,245,0.05)" strokeWidth={1.5} dot={false} name="Close" />
                {showSma && pts.some(p => p.sma != null) && <Line type="monotone" dataKey="sma" stroke="#f5a142" strokeWidth={1.5} dot={false} name={`SMA(${smaPeriod})`} connectNulls={false} />}
                {showEma && pts.some(p => p.ema != null) && <Line type="monotone" dataKey="ema" stroke="#b066f5" strokeWidth={1.5} dot={false} name={`EMA(${emaPeriod})`} connectNulls={false} />}
                {showBb && pts.some(p => p.bb_upper != null) && (
                  <>
                    <Line type="monotone" dataKey="bb_upper" stroke="#42f5a1" strokeWidth={1} dot={false} name="BB Upper" strokeDasharray="4 2" connectNulls={false} />
                    <Line type="monotone" dataKey="bb_lower" stroke="#42f5a1" strokeWidth={1} dot={false} name="BB Lower" strokeDasharray="4 2" connectNulls={false} />
                  </>
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" style={{ background: "var(--accent2)" }} />RSI ({rsiPeriod})</div>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={pts} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTip />} />
                <ReferenceLine y={70} stroke="#f55142" strokeDasharray="4 2" />
                <ReferenceLine y={30} stroke="#42f5a1" strokeDasharray="4 2" />
                <Line type="monotone" dataKey="rsi" stroke="#42d4f5" strokeWidth={1.5} dot={false} name="RSI" connectNulls={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {!loading && !data && (
        <div className="empty"><div className="empty-icon">📈</div><div className="empty-text">Configure indicators above and click Calculate</div></div>
      )}
    </div>
  );
}

// ─── BACKTEST PAGE ────────────────────────────────────────────────────────────
function BacktestPage({ token }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [start, setStart] = useState("2023-01-01");
  const [end, setEnd] = useState(new Date().toISOString().slice(0, 10));
  const [smaPeriod, setSmaPeriod] = useState(20);
  const [initialCash, setInitialCash] = useState(10000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const run = async () => {
    setErr(""); setResult(null); setLoading(true);
    try {
      const data = await apiFetch(
        `/backtest/${symbol.toUpperCase()}?start=${start}&end=${end}&sma_period=${smaPeriod}&initial_cash=${initialCash}`,
        token
      );
      setResult(data);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  const m = result?.metrics;

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Backtester</div>
        <div className="page-sub">SMA threshold strategy — long-only, all-in / all-out</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="grid-2">
          <div className="field"><label>Symbol</label><input value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} /></div>
          <div className="field"><label>Initial Cash ($)</label><input type="number" value={initialCash} onChange={e => setInitialCash(Number(e.target.value))} /></div>
        </div>
        <div className="grid-3">
          <div className="field"><label>Start</label><input type="date" value={start} onChange={e => setStart(e.target.value)} /></div>
          <div className="field"><label>End</label><input type="date" value={end} onChange={e => setEnd(e.target.value)} /></div>
          <div className="field"><label>SMA Period</label><input type="number" value={smaPeriod} onChange={e => setSmaPeriod(Number(e.target.value))} min={1} /></div>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading || !symbol}>
          {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Running…</> : "▶ Run Backtest"}
        </button>
        {err && <div className="err" style={{ marginTop: 8 }}>⚠ {err}</div>}
      </div>

      {result && (
        <>
          <div className="grid-4" style={{ marginBottom: 16 }}>
            {[
              { label: "Total Return", val: fmtPct(m.total_return_pct), cls: m.total_return_pct >= 0 ? "pos" : "neg" },
              { label: "Max Drawdown", val: fmtPct(-m.max_drawdown_pct), cls: "neg" },
              { label: "Win Rate", val: fmtPct(m.win_rate_pct), cls: "pos" },
              { label: "Trades", val: m.num_trades, cls: "neu" },
            ].map(c => (
              <div key={c.label} className="stat-chip">
                <div className="stat-chip-label">{c.label}</div>
                <div className={`stat-chip-val ${c.cls}`}>{c.val}</div>
              </div>
            ))}
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" />Equity Curve</div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={result.equity_curve} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#c8f542" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#c8f542" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
                <Tooltip content={<ChartTip />} />
                <ReferenceLine y={initialCash} stroke="#6b6b80" strokeDasharray="4 2" />
                <Area type="monotone" dataKey="equity" stroke="#c8f542" fill="url(#eq)" strokeWidth={2} dot={false} name="Equity" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {result.trades.length > 0 && (
            <div className="card">
              <div className="card-title"><span className="dot" />Trade Log</div>
              <div style={{ overflowX: "auto" }}>
                <table className="tbl">
                  <thead>
                    <tr>
                      {["Entry", "Exit", "Entry $", "Exit $", "P&L", "Return", "Signal"].map(h => <th key={h}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {result.trades.map((t, i) => (
                      <tr key={i}>
                        <td className="muted">{fmtDate(t.entry_date)}</td>
                        <td className="muted">{fmtDate(t.exit_date)}</td>
                        <td>{fmt(t.entry_price)}</td>
                        <td>{fmt(t.exit_price)}</td>
                        <td className={t.pnl >= 0 ? "pos" : "neg"}>${fmt(t.pnl)}</td>
                        <td className={t.return_pct >= 0 ? "pos" : "neg"}>{fmtPct(t.return_pct)}</td>
                        <td>
                          <span className={`badge ${t.pnl >= 0 ? "badge-buy" : "badge-sell"}`}>
                            {t.pnl >= 0 ? "WIN" : "LOSS"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {!loading && !result && (
        <div className="empty"><div className="empty-icon">⚗️</div><div className="empty-text">Configure and run a backtest to see results</div></div>
      )}
    </div>
  );
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function Dashboard() {
  return (
    <div>
      <div className="page-header">
        <div className="page-title">Dashboard</div>
        <div className="page-sub">Welcome to the Market Signal & Research Platform</div>
      </div>
      <div className="grid-3" style={{ marginBottom: 16 }}>
        {[
          { icon: "📥", title: "Ingest Data", desc: "Pull OHLCV candle data from Stooq for any ticker symbol" },
          { icon: "📊", title: "View Charts", desc: "Explore price history with interactive candlestick charts" },
          { icon: "📈", title: "Indicators", desc: "SMA, EMA, RSI, and Bollinger Bands overlays" },
          { icon: "⚗️", title: "Backtester", desc: "Run SMA threshold strategy with equity curve and trade log" },
        ].map(c => (
          <div key={c.title} className="card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ fontSize: 24 }}>{c.icon}</div>
            <div style={{ fontFamily: "var(--font-head)", fontWeight: 700, fontSize: 15 }}>{c.title}</div>
            <div style={{ color: "var(--muted)", fontSize: 12, lineHeight: 1.5 }}>{c.desc}</div>
          </div>
        ))}
      </div>
      <div className="card">
        <div className="card-title"><span className="dot" />Quick Start</div>
        <ol style={{ paddingLeft: 20, color: "var(--muted)", fontSize: 12, lineHeight: 2 }}>
          <li>Go to <strong style={{ color: "var(--text)" }}>Ingest</strong> → enter a ticker (e.g. AAPL) and a date range → click Ingest</li>
          <li>Go to <strong style={{ color: "var(--text)" }}>Chart</strong> → load candles for your symbol</li>
          <li>Go to <strong style={{ color: "var(--text)" }}>Indicators</strong> → enable overlays and calculate</li>
          <li>Go to <strong style={{ color: "var(--text)" }}>Backtest</strong> → run the SMA strategy and review P&L</li>
        </ol>
      </div>
    </div>
  );
}

// ─── APP ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("msrp_token") || "");
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("msrp_email") || "");
  const [page, setPage] = useState("home");

  const onAuth = (t, email) => {
    setToken(t); setUserEmail(email);
    localStorage.setItem("msrp_token", t);
    localStorage.setItem("msrp_email", email);
    setPage("home");
  };

  const logout = () => {
    setToken(""); setUserEmail("");
    localStorage.removeItem("msrp_token");
    localStorage.removeItem("msrp_email");
  };

  const NAV = [
    { id: "home", label: "Dashboard", icon: "⬡" },
    { id: "ingest", label: "Ingest", icon: "↓" },
    { id: "candles", label: "Chart", icon: "◈" },
    { id: "indicators", label: "Indicators", icon: "∿" },
    { id: "backtest", label: "Backtest", icon: "⚗" },
  ];

  return (
    <>
      <style>{STYLE}</style>
      <div className="app">
        <header className="topbar">
          <div className="logo">MSRP<span>.</span></div>
          {token && (
            <nav className="topbar-nav">
              {NAV.map(n => (
                <button key={n.id} className={`nav-btn${page === n.id ? " active" : ""}`} onClick={() => setPage(n.id)}>
                  {n.label}
                </button>
              ))}
            </nav>
          )}
          <div className="topbar-right">
            {token ? (
              <>
                <div className="user-pill">
                  <span className="user-dot" />
                  {userEmail}
                </div>
                <button className="btn btn-danger" style={{ padding: "5px 14px", fontSize: 11 }} onClick={logout}>Sign Out</button>
              </>
            ) : (
              <div style={{ fontSize: 11, color: "var(--muted)" }}>Not signed in</div>
            )}
          </div>
        </header>

        {!token ? (
          <AuthPage onAuth={onAuth} />
        ) : (
          <div className="main">
            <aside className="sidebar">
              {NAV.map(n => (
                <div key={n.id} className="sidebar-section" style={{ marginBottom: 4 }}>
                  <div className={`sidebar-item${page === n.id ? " active" : ""}`} onClick={() => setPage(n.id)}>
                    <span className="sidebar-icon">{n.icon}</span>
                    {n.label}
                  </div>
                </div>
              ))}
            </aside>
            <main className="content">
              {page === "home" && <Dashboard />}
              {page === "ingest" && <IngestPage token={token} />}
              {page === "candles" && <CandlesPage token={token} />}
              {page === "indicators" && <IndicatorsPage token={token} />}
              {page === "backtest" && <BacktestPage token={token} />}
            </main>
          </div>
        )}
      </div>
    </>
  );
}