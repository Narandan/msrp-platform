import { fmt } from "../utils/Helpers.js";

// ─── CUSTOM TOOLTIP ──────────────────────────────────────────────────────────
// Refactoring: ChartTip on its own could be a bit small for an individual file, but for readability's sake I will leave it as is. 
// Feel free to change that if needed. 
function ChartTip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, display: "flex", gap: 8, justifyContent: "space-between" }}>
          <span>{p.name}</span>
          <span style={{ fontWeight: 600 }}>{fmt(p.value, 4)}</span>
        </div>
      ))}
    </div>
  );
}

export { ChartTip };