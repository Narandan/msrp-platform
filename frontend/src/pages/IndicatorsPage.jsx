import { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, ComposedChart, Area, Bar
} from "recharts";
import { getPersist, setPersist, apiFetch, trackRecentSymbol, isSessionExpiredError } from "../utils/Helpers.js";
import { SymbolAutocomplete } from "../components/SymbolAutocomplete";
import { ChartTip } from "../components/ChartTip";

function IndicatorsPage({ token }) {
  const p = getPersist().indicators || {};

  const [symbol, setSymbol] = useState(p.symbol ?? "AAPL");
  const [start, setStart] = useState(p.start ?? "2024-01-01");
  const [end, setEnd] = useState(p.end ?? new Date().toISOString().slice(0, 10));

  const [smaPeriod, setSmaPeriod] = useState(p.smaPeriod ?? 20);
  const [emaPeriod, setEmaPeriod] = useState(p.emaPeriod ?? 20);
  const [rsiPeriod, setRsiPeriod] = useState(p.rsiPeriod ?? 14);
  const [bbPeriod, setBbPeriod] = useState(p.bbPeriod ?? 20);

  const [macdFast, setMacdFast] = useState(p.macdFast ?? 12);
  const [macdSlow, setMacdSlow] = useState(p.macdSlow ?? 26);
  const [macdSignal, setMacdSignal] = useState(p.macdSignal ?? 9);

  const [showSma, setShowSma] = useState(p.showSma !== false);
  const [showEma, setShowEma] = useState(p.showEma ?? false);
  const [showBb, setShowBb] = useState(p.showBb ?? false);
  const [showRsi, setShowRsi] = useState(p.showRsi ?? false);
  const [showMacd, setShowMacd] = useState(p.showMacd ?? false);

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    setPersist({
      indicators: {
        symbol,
        start,
        end,
        smaPeriod,
        emaPeriod,
        rsiPeriod,
        bbPeriod,
        macdFast,
        macdSlow,
        macdSignal,
        showSma,
        showEma,
        showBb,
        showRsi,
        showMacd,
      },
    });
  }, [
    symbol,
    start,
    end,
    smaPeriod,
    emaPeriod,
    rsiPeriod,
    bbPeriod,
    macdFast,
    macdSlow,
    macdSignal,
    showSma,
    showEma,
    showBb,
    showRsi,
    showMacd,
  ]);

  const load = async () => {
    setErr("");
    setLoading(true);

    try {
      let url = `/indicators/${symbol.toUpperCase()}?start=${start}&end=${end}`;

      if (showSma) url += `&sma_period=${smaPeriod}`;
      if (showEma) url += `&ema_period=${emaPeriod}`;
      if (showBb) url += `&bb_period=${bbPeriod}`;
      if (showRsi) url += `&rsi_period=${rsiPeriod}`;
      if (showMacd) {
        url += `&macd_fast=${macdFast}&macd_slow=${macdSlow}&macd_signal=${macdSignal}`;
      }

      const d = await apiFetch(url, token);
      setData(d);
      trackRecentSymbol(symbol);
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  const pts = data?.points ?? [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Indicators</div>
        <div className="page-sub">SMA, EMA, RSI, Bollinger Bands, MACD for any symbol</div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="grid-2" style={{ marginBottom: 12 }}>
          <SymbolAutocomplete
            value={symbol}
            onChange={setSymbol}
            token={token}
            placeholder="AAPL"
          />

          <div style={{ display: "flex", gap: 8 }}>
            <div className="field" style={{ flex: 1 }}>
              <label>Start</label>
              <input
                type="date"
                value={start}
                onChange={(e) => setStart(e.target.value)}
              />
            </div>

            <div className="field" style={{ flex: 1 }}>
              <label>End</label>
              <input
                type="date"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="pill-row">
          <button
            className={`pill sma${showSma ? " on" : ""}`}
            onClick={() => setShowSma(!showSma)}
          >
            SMA {showSma && `(${smaPeriod})`}
          </button>

          <button
            className={`pill ema${showEma ? " on" : ""}`}
            onClick={() => setShowEma(!showEma)}
          >
            EMA {showEma && `(${emaPeriod})`}
          </button>

          <button
            className={`pill bb${showBb ? " on" : ""}`}
            onClick={() => setShowBb(!showBb)}
          >
            Bollinger {showBb && `(${bbPeriod})`}
          </button>

          <button
            className={`pill rsi${showRsi ? " on" : ""}`}
            onClick={() => setShowRsi(!showRsi)}
          >
            RSI {showRsi && `(${rsiPeriod})`}
          </button>

          <button
            className={`pill macd${showMacd ? " on" : ""}`}
            onClick={() => setShowMacd(!showMacd)}
          >
            MACD {showMacd && `(${macdFast},${macdSlow},${macdSignal})`}
          </button>
        </div>

        {(showSma || showEma || showBb || showRsi || showMacd) && (
          <div className="grid-3" style={{ marginBottom: 12 }}>
            {showSma && (
              <div className="field">
                <label>SMA Period</label>
                <input
                  type="number"
                  value={smaPeriod}
                  onChange={(e) => setSmaPeriod(Number(e.target.value))}
                  min={1}
                />
              </div>
            )}

            {showEma && (
              <div className="field">
                <label>EMA Period</label>
                <input
                  type="number"
                  value={emaPeriod}
                  onChange={(e) => setEmaPeriod(Number(e.target.value))}
                  min={1}
                />
              </div>
            )}

            {showBb && (
              <div className="field">
                <label>BB Period</label>
                <input
                  type="number"
                  value={bbPeriod}
                  onChange={(e) => setBbPeriod(Number(e.target.value))}
                  min={1}
                />
              </div>
            )}

            {showRsi && (
              <div className="field">
                <label>RSI Period</label>
                <input
                  type="number"
                  value={rsiPeriod}
                  onChange={(e) => setRsiPeriod(Number(e.target.value))}
                  min={1}
                />
              </div>
            )}

            {showMacd && (
              <>
                <div className="field">
                  <label>MACD Fast</label>
                  <input
                    type="number"
                    value={macdFast}
                    onChange={(e) => setMacdFast(Number(e.target.value))}
                    min={1}
                  />
                </div>

                <div className="field">
                  <label>MACD Slow</label>
                  <input
                    type="number"
                    value={macdSlow}
                    onChange={(e) => setMacdSlow(Number(e.target.value))}
                    min={1}
                  />
                </div>

                <div className="field">
                  <label>MACD Signal</label>
                  <input
                    type="number"
                    value={macdSignal}
                    onChange={(e) => setMacdSignal(Number(e.target.value))}
                    min={1}
                  />
                </div>
              </>
            )}
          </div>
        )}

        <button className="btn btn-primary" onClick={load} disabled={loading || !symbol}>
          {loading ? (
            <>
              <div className="spinner" style={{ width: 14, height: 14 }} />
              Loading…
            </>
          ) : (
            "Calculate →"
          )}
        </button>

        {err && <div className="err" style={{ marginTop: 8 }}>⚠ {err}</div>}
      </div>

      {pts.length > 0 && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title">
              <span className="dot" />
              {data.symbol} — Price + Overlays
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={pts} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                <YAxis
                  tick={{ fill: "#6b6b80", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  domain={["auto", "auto"]}
                />
                <Tooltip content={<ChartTip />} />
                <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />

                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="#42d4f5"
                  fill="rgba(66,212,245,0.05)"
                  strokeWidth={1.5}
                  dot={false}
                  name="Close"
                />

                {showSma && pts.some((p) => p.sma != null) && (
                  <Line
                    type="monotone"
                    dataKey="sma"
                    stroke="#f5a142"
                    strokeWidth={1.5}
                    dot={false}
                    name={`SMA(${smaPeriod})`}
                    connectNulls={false}
                  />
                )}

                {showEma && pts.some((p) => p.ema != null) && (
                  <Line
                    type="monotone"
                    dataKey="ema"
                    stroke="#b066f5"
                    strokeWidth={1.5}
                    dot={false}
                    name={`EMA(${emaPeriod})`}
                    connectNulls={false}
                  />
                )}

                {showBb && pts.some((p) => p.bb_upper != null) && (
                  <>
                    <Line
                      type="monotone"
                      dataKey="bb_upper"
                      stroke="#42f5a1"
                      strokeWidth={1}
                      dot={false}
                      name="BB Upper"
                      strokeDasharray="4 2"
                      connectNulls={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="bb_lower"
                      stroke="#42f5a1"
                      strokeWidth={1}
                      dot={false}
                      name="BB Lower"
                      strokeDasharray="4 2"
                      connectNulls={false}
                    />
                  </>
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {showRsi && pts.some((p) => p.rsi != null) && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title">
                <span className="dot" style={{ background: "var(--accent2)" }} />
                RSI ({rsiPeriod})
              </div>

              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={pts} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                  <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#6b6b80", fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip content={<ChartTip />} />
                  <ReferenceLine y={70} stroke="#f55142" strokeDasharray="4 2" />
                  <ReferenceLine y={30} stroke="#42f5a1" strokeDasharray="4 2" />
                  <Line
                    type="monotone"
                    dataKey="rsi"
                    stroke="#42d4f5"
                    strokeWidth={1.5}
                    dot={false}
                    name="RSI"
                    connectNulls={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {showMacd && pts.some((p) => p.macd != null || p.macd_signal != null || p.macd_hist != null) && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title">
                <span className="dot" style={{ background: "var(--accent2)" }} />
                MACD ({macdFast}, {macdSlow}, {macdSignal})
              </div>

              <ResponsiveContainer width="100%" height={180}>
                <ComposedChart data={pts} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e24" />
                  <XAxis dataKey="date" tick={{ fill: "#6b6b80", fontSize: 10 }} tickLine={false} />
                  <YAxis
                    tick={{ fill: "#6b6b80", fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    domain={["auto", "auto"]}
                  />
                  <Tooltip content={<ChartTip />} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
                  <Bar dataKey="macd_hist" name="Histogram" fill="#2a2a34" />
                  <Line
                    type="monotone"
                    dataKey="macd"
                    stroke="#42d4f5"
                    strokeWidth={1.5}
                    dot={false}
                    name="MACD"
                    connectNulls={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="macd_signal"
                    stroke="#f5a142"
                    strokeWidth={1.5}
                    dot={false}
                    name="Signal"
                    connectNulls={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {!loading && !data && (
        <div className="empty">
          <div className="empty-icon">📈</div>
          <div className="empty-text">Configure indicators above and click Calculate</div>
        </div>
      )}
    </div>
  );
}

export { IndicatorsPage };