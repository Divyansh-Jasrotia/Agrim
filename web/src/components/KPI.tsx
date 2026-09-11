export function KPI({ label, value, sub, hint, model = false }:
  { label: string; value: string; sub?: string; hint?: string; model?: boolean }) {
  return (
    <div className={`rounded border bg-surface px-4 py-3 ${model ? "border-model" : "border-line"}`}>
      <div className="text-xs uppercase tracking-wide text-muted">{label}{model ? " · model" : ""}</div>
      {/* The figure holds its size. A long currency value is abbreviated by croreShort and the
          exact figure goes on the sub line, instead of shrinking the headline until it fits. */}
      <div className={`num text-2xl font-medium whitespace-nowrap ${model ? "text-model" : ""}`}>{value}</div>
      {sub && <div className="num overflow-hidden text-ellipsis whitespace-nowrap text-xs text-muted">{sub}</div>}
      {hint && <div className="text-xs text-muted">{hint}</div>}
    </div>
  );
}
