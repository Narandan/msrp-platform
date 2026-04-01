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

  /* ── dashboard: symbol chip ── */
  .symbol-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px;
    font-family: var(--font-body); font-size: 12px; font-weight: 600;
    letter-spacing: 0.04em; color: var(--accent);
    background: rgba(200,245,66,0.08);
    border: 1px solid rgba(200,245,66,0.35);
    box-shadow: 0 0 12px rgba(200,245,66,0.08);
  }
  .symbol-chip .market-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); flex-shrink: 0;
  }
  .symbol-chip .market-dot.closed { background: var(--muted); }

  /* ── dashboard: watchlist card ── */
  .watchlist-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .watchlist-card:hover { border-color: var(--border2); box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
  .watchlist-card-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
  .watchlist-card-ticker { font-family: var(--font-body); font-weight: 600; font-size: 14px; color: var(--accent); letter-spacing: 0.04em; }
  .watchlist-card-price { font-size: 13px; color: var(--text); }
  .watchlist-card-change { font-size: 11px; }
  .watchlist-card-change.up { color: var(--green); }
  .watchlist-card-change.down { color: var(--red); }
  .watchlist-card-spark { width: 48px; height: 24px; flex-shrink: 0; }

  /* ── dashboard: quick action tile ── */
  .quick-action-tile {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 10px;
    background: var(--bg); border: 1px solid var(--border2);
    font-family: var(--font-body); font-size: 13px; color: var(--text);
    cursor: pointer; transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
  }
  .quick-action-tile:hover { transform: translateY(-2px); border-color: var(--border); box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
  .quick-action-tile .tile-icon { font-size: 18px; width: 24px; text-align: center; }

  /* ── dashboard: jump back in ── */
  .jump-section-label { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }
  .recent-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
  .recent-row:last-child { margin-bottom: 0; }
  .recent-row .action-links { display: flex; gap: 4px; }
  .recent-row .action-links .btn { padding: 4px 8px; font-size: 10px; }

  /* ── dashboard: portfolio snapshot ── */
  .portfolio-snapshot {
    display: flex; gap: 24px; flex-wrap: wrap; align-items: center;
    padding: 16px 20px; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 20px;
  }
  .portfolio-snapshot-item { display: flex; align-items: baseline; gap: 6px; }
  .portfolio-snapshot-item .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
  .portfolio-snapshot-item .value { font-family: var(--font-head); font-weight: 700; font-size: 16px; color: var(--text); }

  /* responsive */
  @media (max-width: 900px) {
    .sidebar { display: none; }
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  }
`;

// ─── PERSISTENCE (localStorage) ───────────────────────────────────────────────
const PERSIST_KEY = "msrp_persist";

function getPersist() {
  try {
    const raw = localStorage.getItem(PERSIST_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function setPersist(update) {
  try {
    const next = { ...getPersist(), ...update };
    localStorage.setItem(PERSIST_KEY, JSON.stringify(next));
  } catch {
    return;
  }
}

function trackRecentSymbol(symbol) {
  if (!symbol || !symbol.trim()) return;
  const s = symbol.trim().toUpperCase();
  const p = getPersist();
  const recent = p.lastUsedSymbols || [];
  const filtered = [s, ...recent.filter((x) => x !== s)].slice(0, 8);
  setPersist({ ...p, lastUsedSymbols: filtered });
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const fmt = (n, d = 2) =>
  n == null ? "—" : Number(n).toFixed(d);

const fmtPct = (n) =>
  n == null ? "—" : `${n > 0 ? "+" : ""}${Number(n).toFixed(2)}%`;

const fmtDate = (d) => d ? String(d).slice(0, 10) : "—";

/** US market 9:30–16:00 ET, weekdays. Returns { open, countdownText }. */
function getMarketStatus() {
  const now = new Date();
  const et = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
  const day = et.getDay();
  const mins = et.getHours() * 60 + et.getMinutes();
  const OPEN_MINS = 9 * 60 + 30;  // 9:30
  const CLOSE_MINS = 16 * 60;      // 16:00
  const isWeekday = day >= 1 && day <= 5;

  if (!isWeekday) {
    const daysUntilMonday = day === 0 ? 1 : 2;  // Sun -> 1 day, Sat -> 2 days
    const minsUntilOpen = daysUntilMonday * 24 * 60 - mins + OPEN_MINS;
    return { open: false, countdownText: `Opens in ${formatCountdown(minsUntilOpen)}` };
  }
  if (mins < OPEN_MINS) {
    const minsUntilOpen = OPEN_MINS - mins;
    return { open: false, countdownText: `Opens in ${formatCountdown(minsUntilOpen)}` };
  }
  if (mins >= CLOSE_MINS) {
    const minsLeftToday = 24 * 60 - mins;  // minutes until midnight
    // Next open: tomorrow 9:30, or Monday 9:30 if Friday
    const minsUntilNextOpen = day === 5
      ? minsLeftToday + 2 * 24 * 60 + OPEN_MINS   // Fri night -> Mon 9:30
      : minsLeftToday + OPEN_MINS;                 // e.g. Wed 8pm -> Thu 9:30
    return { open: false, countdownText: `Opens in ${formatCountdown(minsUntilNextOpen)}` };
  }
  const minsUntilClose = CLOSE_MINS - mins;
  return { open: true, countdownText: `Closes in ${formatCountdown(minsUntilClose)}` };
}

function formatCountdown(totalMins) {
  if (totalMins <= 0) return "0m";
  const h = Math.floor(totalMins / 60);
  const m = Math.round(totalMins % 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

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

// ─── SYMBOL AUTOCOMPLETE (reusable) ────────────────────────────────────────────
const SEARCH_DEBOUNCE_MS = 180;
const SEARCH_LIMIT = 20;

function SymbolAutocomplete({ value, onChange, placeholder = "AAPL", token, disabled }) {
  const [suggestions, setSuggestions] = useState([]);
  const [showSug, setShowSug] = useState(false);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef(null);

  const fetchSuggestions = useCallback(async (q) => {
    const query = (q || "").trim();
    if (query.length < 1) { setSuggestions([]); setLoading(false); return; }
    setLoading(true);
    try {
      const res = await apiFetch(`/stocks/search?q=${encodeURIComponent(query)}&limit=${SEARCH_LIMIT}`, token);
      setSuggestions(res);
    } catch { setSuggestions([]); }
    finally { setLoading(false); }
  }, [token]);

  const scheduleSearch = useCallback((q) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!(q || "").trim()) {
      setSuggestions([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    debounceRef.current = setTimeout(() => fetchSuggestions(q), SEARCH_DEBOUNCE_MS);
  }, [fetchSuggestions]);

  useEffect(() => () => { if (debounceRef.current) clearTimeout(debounceRef.current); }, []);

  return (
    <div className="autocomplete-wrap">
      <div className="field" style={{ margin: 0 }}>
        <label>Symbol</label>
        <input
          value={value}
          onChange={e => {
            const v = e.target.value.toUpperCase();
            onChange(v);
            scheduleSearch(v);
            setShowSug(true);
          }}
          onFocus={() => { setShowSug(true); if (value.trim()) scheduleSearch(value); }}
          onBlur={() => setTimeout(() => setShowSug(false), 150)}
          placeholder={placeholder}
          disabled={disabled}
        />
      </div>
      {showSug && (suggestions.length > 0 || loading) && (
        <div className="autocomplete-list">
          {loading && suggestions.length === 0 ? (
            <div className="loading-row" style={{ padding: 12 }}><div className="spinner" /> Searching…</div>
          ) : (
            suggestions.map(s => (
              <div key={s.ticker} className="autocomplete-item" onMouseDown={() => { onChange(s.ticker); setSuggestions([]); }}>
                <span className="autocomplete-ticker">{s.ticker}</span>
                {s.name && <span className="autocomplete-name">{s.name}</span>}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

// ─── INGEST PAGE ──────────────────────────────────────────────────────────────
function IngestPage({ token }) {
  const p = getPersist().ingest || {};
  const [symbol, setSymbol] = useState(p.symbol ?? "");
  const [start, setStart] = useState(p.start ?? "2024-01-01");
  const [end, setEnd] = useState(p.end ?? new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    setPersist({ ingest: { symbol, start, end } });
  }, [symbol, start, end]);

  const run = async () => {
    setErr(""); setResult(null); setLoading(true);
    try {
      const data = await apiFetch(`/stocks/${symbol.toUpperCase()}/ingest?start=${start}&end=${end}`, token, { method: "POST" });
      setResult(data);
      trackRecentSymbol(symbol);
      setPersist({ lastIngestedDate: new Date().toISOString().slice(0, 10) });
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
        <SymbolAutocomplete value={symbol} onChange={setSymbol} token={token} placeholder="AAPL" />
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
  const p = getPersist().candles || {};
  const [symbol, setSymbol] = useState(p.symbol ?? "AAPL");
  const [limit, setLimit] = useState(p.limit ?? 200);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    setPersist({ candles: { symbol, limit } });
  }, [symbol, limit]);

  const load = async () => {
    setErr(""); setLoading(true);
    try {
      const d = await apiFetch(`/stocks/${symbol.toUpperCase()}/candles?limit=${limit}`, token);
      setData(d);
      trackRecentSymbol(symbol);
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
          <SymbolAutocomplete value={symbol} onChange={setSymbol} token={token} placeholder="AAPL" />
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
      <NewsPanel symbol={symbol} token={token} />
    </div>
  );
}

// ─── INDICATORS PAGE ──────────────────────────────────────────────────────────
function IndicatorsPage({ token }) {
  const p = getPersist().indicators || {};
  const [symbol, setSymbol] = useState(p.symbol ?? "AAPL");
  const [start, setStart] = useState(p.start ?? "2024-01-01");
  const [end, setEnd] = useState(p.end ?? new Date().toISOString().slice(0, 10));
  const [smaPeriod, setSmaPeriod] = useState(p.smaPeriod ?? 20);
  const [emaPeriod, setEmaPeriod] = useState(p.emaPeriod ?? 20);
  const [rsiPeriod] = useState(p.rsiPeriod ?? 14);
  const [bbPeriod, setBbPeriod] = useState(p.bbPeriod ?? 20);
  const [showSma, setShowSma] = useState(p.showSma !== false);
  const [showEma, setShowEma] = useState(p.showEma ?? false);
  const [showBb, setShowBb] = useState(p.showBb ?? false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    setPersist({
      indicators: { symbol, start, end, smaPeriod, emaPeriod, rsiPeriod, bbPeriod, showSma, showEma, showBb },
    });
  }, [symbol, start, end, smaPeriod, emaPeriod, rsiPeriod, bbPeriod, showSma, showEma, showBb]);

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
      trackRecentSymbol(symbol);
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
          <SymbolAutocomplete value={symbol} onChange={setSymbol} token={token} placeholder="AAPL" />
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

// ─── NEWS PANEL ───────────────────────────────────────────────────────────────
function NewsPanel({ symbol, token }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!symbol) return;
    let cancelled = false;
    queueMicrotask(() => {
      if (cancelled) return;
      setLoading(true); setErr(null);
      apiFetch(`/news/${encodeURIComponent(symbol)}?limit=8`, token)
        .then(d => {
          if (cancelled) return;
          setArticles(d.articles || []);
          setErr(null);
        })
        .catch(e => {
          if (cancelled) return;
          setErr(e.message);
          setArticles([]);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    });
    return () => { cancelled = true; };
  }, [symbol, token]);

  if (!symbol) return null;
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div className="card-title"><span className="dot" style={{ background: "var(--orange)" }} />News — {symbol}</div>
      {loading && <div className="loading-row"><div className="spinner" /> Loading news…</div>}
      {err && <div className="err">⚠ {err}</div>}
      {!loading && !err && articles.length === 0 && <div className="empty"><div className="empty-text">No headlines found</div></div>}
      {!loading && articles.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {articles.map((a, i) => (
            <li key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
              <a href={a.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent2)", fontSize: 12 }}>{a.title}</a>
              {a.source && <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>{a.source}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── WATCHLIST PAGE ───────────────────────────────────────────────────────────
function WatchlistPage({ token }) {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [addTicker, setAddTicker] = useState("");
  const [addLoading, setAddLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true); setErr("");
    try {
      const data = await apiFetch("/watchlist", token);
      setSymbols(data.symbols || []);
    } catch (e) { setErr(e.message); setSymbols([]); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const addSymbol = async () => {
    const t = addTicker.trim().toUpperCase();
    if (!t) return;
    setAddLoading(true); setErr("");
    try {
      await apiFetch("/watchlist", token, { method: "POST", body: JSON.stringify({ ticker: t }) });
      setAddTicker("");
      load();
    } catch (e) { setErr(e.message); }
    finally { setAddLoading(false); }
  };

  const removeSymbol = async (ticker) => {
    try {
      await apiFetch(`/watchlist/${encodeURIComponent(ticker)}`, token, { method: "DELETE" });
      load();
    } catch (e) { setErr(e.message); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Watchlist</div>
        <div className="page-sub">Track symbols and quick-add to analysis</div>
      </div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title"><span className="dot" />Add symbol</div>
        <div className="search-row">
          <div className="field" style={{ flex: 1, margin: 0 }}>
            <label>Ticker</label>
            <input value={addTicker} onChange={e => setAddTicker(e.target.value.toUpperCase())} placeholder="AAPL" />
          </div>
          <button className="btn btn-primary" onClick={addSymbol} disabled={addLoading || !addTicker.trim()}>
            {addLoading ? "Adding…" : "Add"}
          </button>
        </div>
        {err && <div className="err" style={{ marginTop: 8 }}>⚠ {err}</div>}
      </div>
      <div className="card">
        <div className="card-title"><span className="dot" />Your watchlist</div>
        {loading && <div className="loading-row"><div className="spinner" /> Loading…</div>}
        {!loading && symbols.length === 0 && <div className="empty"><div className="empty-text">No symbols. Add a ticker above (must be ingested first).</div></div>}
        {!loading && symbols.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {symbols.map(s => (
              <div key={s.ticker} className="stat-chip" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="autocomplete-ticker">{s.ticker}</span>
                {s.name && <span className="autocomplete-name">{s.name}</span>}
                <button type="button" className="btn btn-ghost" style={{ padding: "2px 8px", fontSize: 11 }} onClick={() => removeSymbol(s.ticker)}>Remove</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── BACKTEST PAGE ────────────────────────────────────────────────────────────
function BacktestPage({ token }) {
  const p = getPersist().backtest || {};
  const [symbol, setSymbol] = useState(p.symbol ?? "AAPL");
  const [start, setStart] = useState(p.start ?? "2023-01-01");
  const [end, setEnd] = useState(p.end ?? new Date().toISOString().slice(0, 10));
  const [strategy, setStrategy] = useState(p.strategy ?? "sma_threshold");
  const [smaPeriod, setSmaPeriod] = useState(p.smaPeriod ?? 20);
  const [fastPeriod, setFastPeriod] = useState(p.fastPeriod ?? 10);
  const [slowPeriod, setSlowPeriod] = useState(p.slowPeriod ?? 20);
  const [initialCash, setInitialCash] = useState(p.initialCash ?? 10000);
  const [transactionCostPct, setTransactionCostPct] = useState(p.transactionCostPct ?? 0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    setPersist({
      backtest: {
        symbol,
        start,
        end,
        strategy,
        smaPeriod,
        fastPeriod,
        slowPeriod,
        initialCash,
        transactionCostPct,
      },
    });
  }, [symbol, start, end, strategy, smaPeriod, fastPeriod, slowPeriod, initialCash, transactionCostPct]);

  const run = async () => {
    setErr(""); setResult(null); setLoading(true);
    try {
      let url = `/backtest/${symbol.toUpperCase()}?start=${start}&end=${end}&strategy=${strategy}&initial_cash=${initialCash}&transaction_cost_pct=${transactionCostPct / 10000}`;
      if (strategy === "sma_threshold") url += `&sma_period=${smaPeriod}`;
      else url += `&fast_period=${fastPeriod}&slow_period=${slowPeriod}`;
      const data = await apiFetch(url, token);
      setResult(data);
      trackRecentSymbol(symbol);
      setPersist({
        lastBacktest: {
          symbol,
          totalReturnPct: data?.metrics?.total_return_pct,
          numTrades: data?.metrics?.num_trades,
        },
      });
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  const m = result?.metrics;

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Backtester</div>
        <div className="page-sub">SMA threshold or SMA crossover — long-only, all-in / all-out</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="grid-2">
          <SymbolAutocomplete value={symbol} onChange={setSymbol} token={token} placeholder="AAPL" />
          <div className="field"><label>Initial Cash ($)</label><input type="number" value={initialCash} onChange={e => setInitialCash(Number(e.target.value))} /></div>
        </div>
        <div className="tabs" style={{ marginTop: 12 }}>
          <button className={`tab-btn${strategy === "sma_threshold" ? " active" : ""}`} onClick={() => setStrategy("sma_threshold")}>SMA threshold</button>
          <button className={`tab-btn${strategy === "sma_crossover" ? " active" : ""}`} onClick={() => setStrategy("sma_crossover")}>SMA crossover</button>
        </div>
        {strategy === "sma_threshold" && (
          <div className="field"><label>SMA Period</label><input type="number" value={smaPeriod} onChange={e => setSmaPeriod(Number(e.target.value))} min={1} /></div>
        )}
        {strategy === "sma_crossover" && (
          <div className="grid-2">
            <div className="field"><label>Fast SMA period</label><input type="number" value={fastPeriod} onChange={e => setFastPeriod(Number(e.target.value))} min={1} /></div>
            <div className="field"><label>Slow SMA period</label><input type="number" value={slowPeriod} onChange={e => setSlowPeriod(Number(e.target.value))} min={1} /></div>
          </div>
        )}
        <div className="field" style={{ marginTop: 8 }}>
          <label>Transaction cost (bps, e.g. 10 = 0.1%)</label>
          <input type="number" value={transactionCostPct} onChange={e => setTransactionCostPct(Number(e.target.value) || 0)} min={0} step={1} />
        </div>
        <div className="grid-2" style={{ marginTop: 12 }}>
          <div className="field"><label>Start</label><input type="date" value={start} onChange={e => setStart(e.target.value)} /></div>
          <div className="field"><label>End</label><input type="date" value={end} onChange={e => setEnd(e.target.value)} /></div>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading || !symbol} style={{ marginTop: 16 }}>
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
              ...(m.sharpe_ratio != null ? [{ label: "Sharpe", val: fmt(m.sharpe_ratio, 2), cls: "neu" }] : []),
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

// ─── Mini sparkline (placeholder) ─────────────────────────────────────────────
function MiniSparkline({ up }) {
  const points = up ? [8, 12, 10, 18] : [18, 14, 16, 10];
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  const w = 48; const h = 24;
  const path = points.map((p, i) => `${(i / (points.length - 1)) * w},${h - ((p - min) / range) * (h - 2) - 1}`).join(" L ");
  return (
    <svg className="watchlist-card-spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <path fill="none" stroke={up ? "var(--green)" : "var(--red)"} strokeWidth="1.5" strokeOpacity={0.8} d={`M ${path}`} />
    </svg>
  );
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function Dashboard({ token, userEmail, setPage }) {
  const [watchlist, setWatchlist] = useState([]);
  const [showHelp, setShowHelp] = useState(false);
  const [marketOpen, setMarketOpen] = useState(true);
  const [marketCountdown, setMarketCountdown] = useState("");
  const persist = getPersist();
  const recentSymbols = persist.lastUsedSymbols || [];
  const lastBacktest = persist.lastBacktest;

  useEffect(() => {
    if (!token) return;
    apiFetch("/watchlist", token)
      .then((d) => setWatchlist(d.symbols || []))
      .catch(() => setWatchlist([]));
  }, [token]);
  useEffect(() => {
    const update = () => {
      const s = getMarketStatus();
      setMarketOpen(s.open);
      setMarketCountdown(s.countdownText);
    };
    update();
    const id = setInterval(update, 60 * 1000);
    return () => clearInterval(id);
  }, []);

  const goToChart = (sym) => {
    setPersist({ candles: { ...getPersist().candles, symbol: sym || recentSymbols[0] } });
    setPage("candles");
  };
  const goToIndicators = (sym) => {
    setPersist({ indicators: { ...getPersist().indicators, symbol: sym || recentSymbols[0] } });
    setPage("indicators");
  };
  const goToBacktest = (sym) => {
    setPersist({ backtest: { ...getPersist().backtest, symbol: sym || recentSymbols[0] } });
    setPage("backtest");
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          {userEmail ? `Hi, ${userEmail.split("@")[0]}` : "Dashboard"}
        </div>
        <div className="page-sub">
          {userEmail ? "Here’s your overview and quick links." : "Welcome to the Market Signal & Research Platform"}
        </div>
      </div>

      {/* Market status + countdown */}
      <div className="portfolio-snapshot">
        <div className="portfolio-snapshot-item">
          <span className="label">Market</span>
          <span className="value" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className={`market-dot ${marketOpen ? "" : "closed"}`} />
            {marketOpen ? "Open" : "Closed"}
            <span className="muted" style={{ fontWeight: 400, fontSize: 13 }}>· {marketCountdown}</span>
          </span>
        </div>
      </div>

      {/* Watchlist as cards */}
      {watchlist.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title"><span className="dot" />Your Watchlist</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 14 }}>
            {watchlist.slice(0, 6).map((s, i) => (
              <div
                key={s.ticker}
                role="button"
                tabIndex={0}
                className="watchlist-card"
                onClick={() => goToChart(s.ticker)}
                onKeyDown={(e) => e.key === "Enter" && goToChart(s.ticker)}
              >
                <div className="watchlist-card-left">
                  <MiniSparkline up={i % 2 === 0} />
                  <div>
                    <div className="watchlist-card-ticker">{s.ticker}</div>
                    <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 2 }}>
                      <span className="watchlist-card-price">—</span>
                      <span className={`watchlist-card-change ${i % 2 === 0 ? "up" : "down"}`}>—</span>
                    </div>
                  </div>
                </div>
                <span className="muted" style={{ fontSize: 11 }}>View chart →</span>
              </div>
            ))}
          </div>
          <button type="button" className="btn btn-ghost" style={{ fontSize: 11 }} onClick={() => setPage("watchlist")}>
            Manage watchlist →
          </button>
        </div>
      )}

      {/* Jump back in */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="jump-section-label">Jump back in</div>
        {recentSymbols.length > 0 && (
          <div style={{ marginBottom: 18 }}>
            {recentSymbols.slice(0, 6).map((sym) => (
              <div key={sym} className="recent-row">
                <span className="symbol-chip">
                  <span className={`market-dot ${marketOpen ? "" : "closed"}`} />
                  {sym}
                </span>
                <div className="action-links">
                  <button type="button" className="btn btn-ghost" onClick={() => goToChart(sym)}>Chart</button>
                  <button type="button" className="btn btn-ghost" onClick={() => goToIndicators(sym)}>Indicators</button>
                  <button type="button" className="btn btn-ghost" onClick={() => goToBacktest(sym)}>Backtest</button>
                </div>
              </div>
            ))}
          </div>
        )}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center" }}>
          <button type="button" className="btn btn-primary" onClick={() => setPage("ingest")} style={{ flexShrink: 0 }}>↓ Ingest data</button>
          <button type="button" className="quick-action-tile" onClick={() => goToChart()}>
            <span className="tile-icon">◈</span><span>Chart</span>
          </button>
          <button type="button" className="quick-action-tile" onClick={() => goToIndicators()}>
            <span className="tile-icon">∿</span><span>Indicators</span>
          </button>
          <button type="button" className="quick-action-tile" onClick={() => goToBacktest()}>
            <span className="tile-icon">⚗</span><span>Backtest</span>
          </button>
        </div>
      </div>

      {/* Last backtest with symbol chip */}
      {lastBacktest?.symbol && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title"><span className="dot" style={{ background: "var(--orange)" }} />Last backtest</div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <span className="symbol-chip">
              <span className={`market-dot ${marketOpen ? "" : "closed"}`} />
              {lastBacktest.symbol}
            </span>
            {lastBacktest.totalReturnPct != null && (
              <span className={lastBacktest.totalReturnPct >= 0 ? "pos" : "neg"} style={{ fontWeight: 600 }}>{fmtPct(lastBacktest.totalReturnPct)}</span>
            )}
            {lastBacktest.numTrades != null && <span className="muted">{lastBacktest.numTrades} trades</span>}
            <button type="button" className="btn btn-ghost" style={{ marginLeft: "auto" }} onClick={() => goToBacktest(lastBacktest.symbol)}>Run again →</button>
          </div>
        </div>
      )}

      {/* Collapsible help */}
      <div className="card">
        <button
          type="button"
          className="card-title"
          onClick={() => setShowHelp((h) => !h)}
          style={{ width: "100%", textAlign: "left", cursor: "pointer", border: "none", background: "none", color: "inherit" }}
        >
          <span className="dot" style={{ background: "var(--muted)" }} />
          {showHelp ? "Hide" : "Show"} quick start guide
        </button>
        {showHelp && (
          <ol style={{ paddingLeft: 20, color: "var(--muted)", fontSize: 12, lineHeight: 2 }}>
            <li>Go to <strong style={{ color: "var(--text)" }}>Ingest</strong> → enter a ticker and date range → click Ingest</li>
            <li>Go to <strong style={{ color: "var(--text)" }}>Chart</strong> → load candles for your symbol</li>
            <li>Go to <strong style={{ color: "var(--text)" }}>Indicators</strong> → enable overlays and calculate</li>
            <li>Go to <strong style={{ color: "var(--text)" }}>Backtest</strong> → run the strategy and review P&L</li>
          </ol>
        )}
      </div>
    </div>
  );
}

// ─── APP ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("msrp_token") || "");
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("msrp_email") || "");
  const [page, setPage] = useState(() => {
    const p = getPersist();
    return p.page && ["home", "watchlist", "ingest", "candles", "indicators", "backtest"].includes(p.page) ? p.page : "home";
  });

  useEffect(() => {
    setPersist({ page });
  }, [page]);

  const onAuth = useCallback((t, email) => {
    setToken(t); setUserEmail(email);
    localStorage.setItem("msrp_token", t);
    localStorage.setItem("msrp_email", email);
    setPage("home");
  }, []);

  const logout = useCallback(() => {
    setToken(""); setUserEmail("");
    localStorage.removeItem("msrp_token");
    localStorage.removeItem("msrp_email");
  }, []);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    apiFetch("/auth/me", token)
      .catch(() => {
        if (!cancelled) logout();
      });
    return () => { cancelled = true; };
  }, [token, logout]);

  const NAV = [
    { id: "home", label: "Dashboard", icon: "⬡" },
    { id: "watchlist", label: "Watchlist", icon: "★" },
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
              {page === "home" && <Dashboard token={token} userEmail={userEmail} setPage={setPage} />}
              {page === "watchlist" && <WatchlistPage token={token} />}
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