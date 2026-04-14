import { useState, useEffect } from "react";
import {
  Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, ComposedChart
} from "recharts";
import { getPersist, setPersist, apiFetch, trackRecentSymbol, fmt, fmtPct, fmtDate, isSessionExpiredError } from "../utils/Helpers.js";
import { SymbolAutocomplete } from "../components/SymbolAutocomplete";
import { ChartTip } from "../components/ChartTip";

// ─── BACKTEST PAGE ────────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
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
  const [stopLossPct, setStopLossPct] = useState(p.stopLossPct ?? 0);
  const [takeProfitPct, setTakeProfitPct] = useState(p.takeProfitPct ?? 0);
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
        stopLossPct,
        takeProfitPct,
      },
    });
  }, [symbol, start, end, strategy, smaPeriod, fastPeriod, slowPeriod, initialCash, transactionCostPct, stopLossPct, takeProfitPct]);

  const run = async () => {
    setErr(""); setResult(null); setLoading(true);
    try {
      const sl = Number(stopLossPct) || 0;
      const tp = Number(takeProfitPct) || 0;
      let url = `/backtest/${symbol.toUpperCase()}?start=${start}&end=${end}&strategy=${strategy}&initial_cash=${initialCash}&transaction_cost_pct=${transactionCostPct / 10000}&stop_loss_pct=${sl / 100}&take_profit_pct=${tp / 100}`;
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
    } catch (e) {
      if (isSessionExpiredError(e)) return;
      setErr(e.message);
    }
    finally { setLoading(false); }
  };

  const m = result?.metrics;
  const b = result?.benchmark;
  const chartData = result
    ? result.equity_curve.map((pt, i) => ({
        date: pt.date,
        equity: pt.equity,
        buyHold: result.benchmark?.equity_curve?.[i]?.equity,
      }))
    : [];

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
        <div className="grid-2" style={{ marginTop: 8 }}>
          <div className="field">
            <label>Stop-loss (% of entry, 0 = off)</label>
            <input type="number" value={stopLossPct} onChange={e => setStopLossPct(Number(e.target.value) || 0)} min={0} max={100} step={0.1} />
          </div>
          <div className="field">
            <label>Take-profit (% of entry, 0 = off)</label>
            <input type="number" value={takeProfitPct} onChange={e => setTakeProfitPct(Number(e.target.value) || 0)} min={0} step={0.1} />
          </div>
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

          {b && (
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title"><span className="dot" style={{ background: "var(--accent2)" }} />Buy &amp; hold benchmark</div>
              <div className="page-sub" style={{ marginBottom: 12 }}>Same symbol and date range — full cash at first close, then hold.</div>
              <div className="grid-4">
                {[
                  { label: "Total Return", val: fmtPct(b.total_return_pct), cls: b.total_return_pct >= 0 ? "pos" : "neg" },
                  { label: "CAGR", val: fmtPct(b.cagr_pct), cls: b.cagr_pct >= 0 ? "pos" : "neg" },
                  { label: "Sharpe", val: fmt(b.sharpe_ratio, 2), cls: "neu" },
                ].map(c => (
                  <div key={c.label} className="stat-chip">
                    <div className="stat-chip-label">{c.label}</div>
                    <div className={`stat-chip-val ${c.cls}`}>{c.val}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title"><span className="dot" />Equity Curve</div>
            <ResponsiveContainer width="100%" height={280}>
              <ComposedChart data={chartData} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
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
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <ReferenceLine y={initialCash} stroke="#6b6b80" strokeDasharray="4 2" />
                <Area type="monotone" dataKey="equity" stroke="#c8f542" fill="url(#eq)" strokeWidth={2} dot={false} name="Strategy" />
                {b && (
                  <Line type="monotone" dataKey="buyHold" stroke="#8899ff" strokeWidth={2} dot={false} name="Buy & hold" />
                )}
              </ComposedChart>
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

// Change added
export { BacktestPage };