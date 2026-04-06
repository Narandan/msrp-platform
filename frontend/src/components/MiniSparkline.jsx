// ─── Mini sparkline (placeholder) ─────────────────────────────────────────────
// Refactoring: Same note as ChartTip.jsx. 
function MiniSparkline({ up }) {
  const points = up ? [8, 12, 10, 18] : [18, 14, 16, 10];
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  const w = 48; const h = 24;
  const path = points.map((p, i) => `${(i / (points.length - 1)) * w},${h - ((p - min) / range) * (h - 2) - 1}`).join(" L ");
  return (
    <svg className="watchlist-card-spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <path fill="none" stroke={up ? "var(--green)" : "var(--red)"} strokeWidth="1.5" strokeOpacity={0.8} d={`M ${path}`} />
    </svg>
  );
}

export { MiniSparkline };