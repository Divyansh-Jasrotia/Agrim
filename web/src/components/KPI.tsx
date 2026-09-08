export function KPI({ label, value, hint, model = false }: { label: string; value: string; hint?: string; model?: boolean }) {
  return (
    <div className={`rounded border bg-surface px-4 py-3 ${model ? "border-model" : "border-line"}`}>
      <div className="text-xs uppercase tracking-wide text-muted">{label}{model ? " · model" : ""}</div>
      {/* text-2xl is the cap; the clamp lets a 12-digit crore figure shrink to fit instead of being clipped by the card. */}
      <div className={`num text-2xl [font-size:clamp(1rem,1.4vw,1.5rem)] font-medium ${model ? "text-model" : ""}`}>{value}</div>
      {hint && <div className="text-xs text-muted">{hint}</div>}
    </div>
  );
}
