import { useState, useEffect } from "react";
import { getPersist, setPersist, apiFetch, getMarketStatus, fmtPct, isSessionExpiredError } from "../utils/Helpers.js";
import { MiniSparkline } from "../components/MiniSparkline";

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 1 change was made to the original code 
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
      .catch((e) => {
        if (isSessionExpiredError(e)) return;
        setWatchlist([]);
      });
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

// Change added
export { Dashboard };