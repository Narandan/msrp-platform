import { useState, useEffect } from "react";
import { getPersist, setPersist, apiFetch, trackRecentSymbol, isSessionExpiredError } from "../utils/Helpers.js";
import { SymbolAutocomplete } from "../components/SymbolAutocomplete";

// ─── INGEST PAGE ──────────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
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
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message);
    }
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

// Change added
export { IngestPage };