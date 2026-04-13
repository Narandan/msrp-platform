// ─── STYLES ──────────────────────────────────────────────────────────────────
// Refactoring: The styles will be moved from App.jsx to a seperate file, though it is still over 300 lines.
// This will hopefully make them easier to maintain and out of the way. 
const STYLE = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #09090b;
    --surface:  #111114;
    --border:   #1e1e24;
    --border2:  #2a2a34;
    --text:     #e8e8f0;
    --muted:    #6b6b80;
    --accent:   #c8f542;
    --accent2:  #42d4f5;
    --red:      #f55142;
    --green:    #42f5a1;
    --orange:   #f5a142;
    --font-body: 'DM Mono', monospace;
    --font-head: 'Syne', sans-serif;
    --radius:   6px;
  }

  html, body, #root { height: 100%; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 13px;
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

  /* layout */
  .app { display: flex; flex-direction: column; min-height: 100vh; }

  /* ── topbar ── */
  .topbar {
    display: flex; align-items: center; gap: 24px;
    padding: 0 28px; height: 56px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky; top: 0; z-index: 100;
  }
  .logo {
    font-family: var(--font-head);
    font-size: 18px; font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--accent);
  }
  .logo span { color: var(--text); }
  .topbar-nav { display: flex; gap: 2px; margin-left: 16px; }
  .nav-btn {
    background: none; border: none; cursor: pointer;
    padding: 6px 14px; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px;
    color: var(--muted); letter-spacing: 0.04em;
    transition: all 0.15s;
  }
  .nav-btn:hover { color: var(--text); background: var(--border); }
  .nav-btn.active { color: var(--accent); background: rgba(200,245,66,0.08); }
  .topbar-right { margin-left: auto; display: flex; align-items: center; gap: 12px; }
  .user-pill {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 12px; background: var(--border); border-radius: 20px;
    font-size: 11px; color: var(--muted);
  }
  .user-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }

  /* ── auth ── */
  .auth-wrap {
    flex: 1; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(ellipse at 50% 0%, rgba(200,245,66,0.04) 0%, transparent 60%);
  }
  .auth-box {
    width: 380px; padding: 40px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    animation: fadeUp 0.4s ease;
  }
  .auth-title {
    font-family: var(--font-head); font-size: 26px; font-weight: 800;
    margin-bottom: 4px;
  }
  .auth-notice {
    font-size: 12px;
    line-height: 1.45;
    margin: -4px 0 20px;
    padding: 12px 14px;
    border-radius: 8px;
    background: rgba(200,245,66,0.1);
    border: 1px solid rgba(200,245,66,0.35);
    color: var(--fg);
  }
  .auth-sub { color: var(--muted); font-size: 12px; margin-bottom: 28px; }
  .auth-tabs { display: flex; gap: 4px; margin-bottom: 28px; }
  .auth-tab {
    flex: 1; padding: 8px; border: 1px solid var(--border2);
    background: none; cursor: pointer; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px; color: var(--muted);
    transition: all 0.15s;
  }
  .auth-tab.active { border-color: var(--accent); color: var(--accent); background: rgba(200,245,66,0.06); }

  /* ── form ── */
  .field { margin-bottom: 16px; }
  .field label { display: block; font-size: 11px; color: var(--muted); margin-bottom: 6px; letter-spacing: 0.06em; text-transform: uppercase; }
  .field input, .field select {
    width: 100%; padding: 10px 12px;
    background: var(--bg); border: 1px solid var(--border2);
    border-radius: var(--radius); color: var(--text);
    font-family: var(--font-body); font-size: 13px;
    outline: none; transition: border 0.15s;
    appearance: none;
  }
  .field input:focus, .field select:focus { border-color: var(--accent); }
  .btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    padding: 10px 20px; border: none; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 13px; cursor: pointer;
    transition: all 0.15s; font-weight: 500;
  }
  .btn-primary {
    background: var(--accent); color: var(--bg);
    width: 100%;
  }
  .btn-primary:hover { opacity: 0.88; }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-ghost {
    background: var(--border); color: var(--text);
  }
  .btn-ghost:hover { background: var(--border2); }
  .btn-danger {
    background: rgba(245,81,66,0.12); color: var(--red); border: 1px solid rgba(245,81,66,0.3);
  }
  .btn-danger:hover { background: rgba(245,81,66,0.2); }
  .err { color: var(--red); font-size: 12px; margin-top: 12px; }

  /* ── main content ── */
  .main { flex: 1; display: flex; }
  .sidebar {
    width: 240px; min-height: 0;
    border-right: 1px solid var(--border);
    background: var(--surface);
    display: flex; flex-direction: column;
    padding: 20px 0;
    position: sticky; top: 56px; height: calc(100vh - 56px);
    overflow-y: auto;
  }
  .sidebar-section { padding: 0 16px; margin-bottom: 24px; }
  .sidebar-label {
    font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 8px; padding: 0 4px;
  }
  .sidebar-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: var(--radius);
    cursor: pointer; transition: all 0.12s;
    font-size: 12px; color: var(--muted);
    border: 1px solid transparent;
  }
  .sidebar-item:hover { background: var(--border); color: var(--text); }
  .sidebar-item.active {
    background: rgba(200,245,66,0.07);
    border-color: rgba(200,245,66,0.2);
    color: var(--accent);
  }
  .sidebar-icon { font-size: 14px; width: 18px; text-align: center; }
  .content { flex: 1; padding: 28px; overflow-y: auto; }

  /* ── page titles ── */
  .page-header { margin-bottom: 28px; }
  .page-title {
    font-family: var(--font-head); font-size: 24px; font-weight: 800;
    margin-bottom: 4px;
  }
  .page-sub { color: var(--muted); font-size: 12px; }

  /* ── cards ── */
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 24px;
    animation: fadeUp 0.3s ease;
  }
  .card-title {
    font-family: var(--font-head); font-size: 14px; font-weight: 700;
    margin-bottom: 18px; color: var(--text);
    display: flex; align-items: center; gap: 8px;
  }
  .card-title .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent);
  }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }

  /* ── stat chips ── */
  .stat-chip {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px;
  }
  .stat-chip-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
  .stat-chip-val { font-size: 22px; font-family: var(--font-head); font-weight: 700; }
  .stat-chip-val.pos { color: var(--green); }
  .stat-chip-val.neg { color: var(--red); }
  .stat-chip-val.neu { color: var(--accent2); }

  /* ── symbol search ── */
  .search-row { display: flex; gap: 8px; align-items: flex-end; flex-wrap: wrap; }
  .search-row .field { margin: 0; flex: 1; min-width: 120px; }
  .autocomplete-wrap { position: relative; flex: 1; min-width: 120px; }
  .autocomplete-list {
    position: absolute; top: calc(100% + 4px); left: 0; right: 0;
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: var(--radius); z-index: 50;
    max-height: 180px; overflow-y: auto;
  }
  .autocomplete-item {
    padding: 8px 12px; cursor: pointer; font-size: 12px;
    display: flex; align-items: center; gap: 8px;
    transition: background 0.1s;
  }
  .autocomplete-item:hover { background: var(--border); }
  .autocomplete-ticker { color: var(--accent); font-weight: 500; }
  .autocomplete-name { color: var(--muted); }

  /* ── table ── */
  .tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
  .tbl th {
    text-align: left; padding: 8px 12px;
    font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); border-bottom: 1px solid var(--border);
    font-weight: 500;
  }
  .tbl td { padding: 9px 12px; border-bottom: 1px solid var(--border); }
  .tbl tr:last-child td { border-bottom: none; }
  .tbl tr:hover td { background: rgba(255,255,255,0.02); }
  .pos { color: var(--green); }
  .neg { color: var(--red); }
  .muted { color: var(--muted); }

  /* ── badge ── */
  .badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 4px; font-size: 10px; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
  }
  .badge-buy { background: rgba(66,245,161,0.12); color: var(--green); }
  .badge-sell { background: rgba(245,81,66,0.12); color: var(--red); }
  .badge-hold { background: rgba(107,107,128,0.2); color: var(--muted); }

  /* ── tooltip ── */
  .chart-tooltip {
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: var(--radius); padding: 10px 14px;
    font-size: 11px;
  }
  .chart-tooltip .label { color: var(--muted); margin-bottom: 4px; }

  /* ── tabs ── */
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }
  .tab-btn {
    background: none; border: 1px solid transparent; cursor: pointer;
    padding: 6px 14px; border-radius: var(--radius);
    font-family: var(--font-body); font-size: 12px; color: var(--muted);
    transition: all 0.15s;
  }
  .tab-btn:hover { color: var(--text); border-color: var(--border2); }
  .tab-btn.active { color: var(--accent); border-color: rgba(200,245,66,0.3); background: rgba(200,245,66,0.06); }

  /* ── spinner ── */
  .spinner {
    width: 20px; height: 20px; border-radius: 50%;
    border: 2px solid var(--border2); border-top-color: var(--accent);
    animation: spin 0.6s linear infinite;
  }
  .loading-row { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 40px; color: var(--muted); font-size: 12px; }

  /* ── empty ── */
  .empty { text-align: center; padding: 48px 24px; color: var(--muted); }
  .empty-icon { font-size: 32px; margin-bottom: 12px; }
  .empty-text { font-size: 13px; }

  /* ── separator ── */
  .sep { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

  /* ── ingest panel ── */
  .ingest-result {
    display: flex; gap: 12px; padding: 14px;
    background: rgba(200,245,66,0.05); border: 1px solid rgba(200,245,66,0.2);
    border-radius: var(--radius); margin-top: 16px;
    font-size: 12px;
  }
  .ingest-result span { color: var(--muted); }
  .ingest-result strong { color: var(--accent); }

  /* ── animations ── */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── indicator toggle pills ── */
  .pill-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
  .pill {
    padding: 4px 12px; border-radius: 20px; font-size: 11px;
    border: 1px solid var(--border2); cursor: pointer;
    transition: all 0.12s; color: var(--muted); background: none;
    font-family: var(--font-body);
  }
  .pill.on { border-color: var(--accent2); color: var(--accent2); background: rgba(66,212,245,0.08); }
  .pill.sma { border-color: var(--orange); color: var(--orange); background: rgba(245,161,66,0.08); }
  .pill.ema { border-color: #b066f5; color: #b066f5; background: rgba(176,102,245,0.08); }
  .pill.rsi { border-color: var(--accent2); color: var(--accent2); background: rgba(66,212,245,0.08); }
  .pill.bb  { border-color: var(--green); color: var(--green); background: rgba(66,245,161,0.08); }

  /* ── dashboard: symbol chip ── */
  .symbol-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px;
    font-family: var(--font-body); font-size: 12px; font-weight: 600;
    letter-spacing: 0.04em; color: var(--accent);
    background: rgba(200,245,66,0.08);
    border: 1px solid rgba(200,245,66,0.35);
    box-shadow: 0 0 12px rgba(200,245,66,0.08);
  }
  .symbol-chip .market-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); flex-shrink: 0;
  }
  .symbol-chip .market-dot.closed { background: var(--muted); }

  /* ── dashboard: watchlist card ── */
  .watchlist-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .watchlist-card:hover { border-color: var(--border2); box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
  .watchlist-card-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
  .watchlist-card-ticker { font-family: var(--font-body); font-weight: 600; font-size: 14px; color: var(--accent); letter-spacing: 0.04em; }
  .watchlist-card-price { font-size: 13px; color: var(--text); }
  .watchlist-card-change { font-size: 11px; }
  .watchlist-card-change.up { color: var(--green); }
  .watchlist-card-change.down { color: var(--red); }
  .watchlist-card-spark { width: 48px; height: 24px; flex-shrink: 0; }

  /* ── dashboard: quick action tile ── */
  .quick-action-tile {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 10px;
    background: var(--bg); border: 1px solid var(--border2);
    font-family: var(--font-body); font-size: 13px; color: var(--text);
    cursor: pointer; transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
  }
  .quick-action-tile:hover { transform: translateY(-2px); border-color: var(--border); box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
  .quick-action-tile .tile-icon { font-size: 18px; width: 24px; text-align: center; }

  /* ── dashboard: jump back in ── */
  .jump-section-label { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }
  .recent-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
  .recent-row:last-child { margin-bottom: 0; }
  .recent-row .action-links { display: flex; gap: 4px; }
  .recent-row .action-links .btn { padding: 4px 8px; font-size: 10px; }

  /* ── dashboard: portfolio snapshot ── */
  .portfolio-snapshot {
    display: flex; gap: 24px; flex-wrap: wrap; align-items: center;
    padding: 16px 20px; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 20px;
  }
  .portfolio-snapshot-item { display: flex; align-items: baseline; gap: 6px; }
  .portfolio-snapshot-item .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
  .portfolio-snapshot-item .value { font-family: var(--font-head); font-weight: 700; font-size: 16px; color: var(--text); }

  /* responsive */
  @media (max-width: 900px) {
    .sidebar { display: none; }
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  }
`;

// Change added
export { STYLE };