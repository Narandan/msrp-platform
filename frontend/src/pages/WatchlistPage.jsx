import { useState, useEffect, useCallback } from "react";
import { apiFetch, isSessionExpiredError } from "../utils/Helpers.js";

// ─── WATCHLIST PAGE ───────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
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
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message); setSymbols([]);
    }
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
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message);
    }
    finally { setAddLoading(false); }
  };

  const removeSymbol = async (ticker) => {
    try {
      await apiFetch(`/watchlist/${encodeURIComponent(ticker)}`, token, { method: "DELETE" });
      load();
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message);
    }
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

// Change added
export { WatchlistPage };