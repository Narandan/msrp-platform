import { useState, useEffect, useCallback } from "react";
import { STYLE } from "./styles/styles.js";
import { getPersist, setPersist, apiFetch } from "./utils/Helpers.js";
import { AuthPage } from "./pages/AuthPage";
import { Dashboard } from "./pages/Dashboard";
import { IngestPage } from "./pages/IngestPage";
import { CandlesPage } from "./pages/CandlesPage";
import { IndicatorsPage } from "./pages/IndicatorsPage";
import { WatchlistPage } from "./pages/WatchlistPage";
import { BacktestPage } from "./pages/BacktestPage";

// ─── MAIN APP ─────────────────────────────────────────────────────
// Refactoring: Any changes to the original made I will mark with comments.
// Note: 2 changes were made to the orignal code, but neither were related to core functionality. 

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
    // Change added: Removal of <<<< Head and ===== a few lines after. Supposedly it's a github conflict with merging.
    // Watch for these in the future. 
    localStorage.removeItem("msrp_persist");
    setPage("home");
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
  // Change added: Removal of >>>> Increment2. Possibly a github conflict marker. 

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