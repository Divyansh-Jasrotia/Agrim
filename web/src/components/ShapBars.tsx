type Factor = { feature: string; contribution: number; value: number | string | null };

const HALF = 50; // the zero line sits at the middle of the bar track

// Bars diverge about a zero line and are normalised to the largest absolute contribution in
// the set, so the widths mean something. The previous version multiplied the contribution by a
// magic pixel factor and capped it, which made two different numbers draw the same bar.
export function ShapBars({ factors }: { factors: Factor[] }) {
  if (!factors.length) return <p className="text-sm text-muted">No factors returned for this project.</p>;
  const max = Math.max(...factors.map((f) => Math.abs(f.contribution)));
  const half = (c: number) => (max === 0 ? 0 : (Math.abs(c) / max) * HALF);
  const fmt = (v: Factor["value"]) => (v == null ? "—" : typeof v === "number" ? v.toFixed(1) : v);
  return (
    <div>
      <ul className="space-y-1">
        {factors.map((f) => {
          const w = half(f.contribution);
          const up = f.contribution >= 0;
          return (
            <li key={f.feature} className="grid grid-cols-[11rem_1fr_5.5rem] items-center gap-2">
              <span className="truncate text-xs text-muted" title={f.feature}>{f.feature}</span>
              <span className="relative block h-3" aria-hidden="true">
                <span className="absolute inset-y-0 left-1/2 w-px bg-line" />
                <span className="absolute inset-y-0.5 rounded-xs bg-model"
                  style={up ? { left: `${HALF}%`, width: `${w}%` } : { right: `${HALF}%`, width: `${w}%` }} />
              </span>
              <span className="num text-right text-xs">
                {up ? "+" : "−"}{Math.abs(f.contribution).toFixed(2)}
                <span className="text-muted"> · {fmt(f.value)}</span>
              </span>
            </li>
          );
        })}
      </ul>
      <p className="mt-2 text-xs text-muted">
        Right of the line increases the predicted probability, left decreases it. Bar length is
        relative to the largest factor shown, and the number after the dot is the project&rsquo;s own
        value for that feature.
      </p>
    </div>
  );
}
