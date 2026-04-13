import { useState, useEffect } from "react";
import { apiFetch, isSessionExpiredError } from "../utils/Helpers.js";

// ─── NEWS PANEL ───────────────────────────────────────────────────────────────
// Refactoring: Like SymbolAutocomplete, NewsPanel will be a seperate file for both length and maintainability. 
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
          if (isSessionExpiredError(e)) return;
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

export { NewsPanel };