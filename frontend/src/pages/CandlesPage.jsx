import { useState, useEffect } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, ComposedChart
} from "recharts";
import { getPersist, setPersist, apiFetch, trackRecentSymbol, fmt, fmtDate } from "../utils/Helpers.js";
import { SymbolAutocomplete } from "../components/SymbolAutocomplete";
import { ChartTip } from "../components/ChartTip";
import { NewsPanel } from "../components/NewsPanel";

// ─── CANDLES PAGE ─────────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
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

// Change added
export { CandlesPage };