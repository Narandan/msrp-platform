import { useState, useEffect, useRef, useCallback } from "react";
import { apiFetch } from "../utils/Helpers.js";

// ─── SYMBOL AUTOCOMPLETE (reusable) ────────────────────────────────────────────
// Refactoring: Autocomplete should remain its own file, due to both length and maintainability.
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

export { SymbolAutocomplete };