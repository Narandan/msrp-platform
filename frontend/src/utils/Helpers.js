// ─── PERSISTENCE (localStorage) ───────────────────────────────────────────────
// Refactoring: Unsure of what to name this file atm, so feel free to edit it.
// Only one change was made to the original code
import { API } from "../config/index.js";

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

/** Called when an authenticated request returns HTTP 401 (expired/invalid token). */
let sessionExpiredHandler = null;

function setSessionExpiredHandler(fn) {
  sessionExpiredHandler = fn;
}

/** True for errors thrown by apiFetch after a 401 with a Bearer token (session no longer valid). */
function isSessionExpiredError(e) {
  return Boolean(e && e.isUnauthorized);
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
    if (res.status === 401 && token) {
      sessionExpiredHandler?.();
      const err = new Error(msg);
      err.isUnauthorized = true;
      throw err;
    }
    throw new Error(msg);
  }
  return res.json();
}

// Change added
export {
  getPersist,
  setPersist,
  trackRecentSymbol,
  fmt,
  fmtPct,
  fmtDate,
  getMarketStatus,
  apiFetch,
  setSessionExpiredHandler,
  isSessionExpiredError,
};