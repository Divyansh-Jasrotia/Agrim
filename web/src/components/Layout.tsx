import { NavLink, Outlet } from "react-router-dom";
import { useBundle } from "../data/store";
import { ExportButton } from "./ExportButton";

const GROUPS: { title: string; items: [string, string][] }[] = [
  { title: "Audit", items: [["/", "Overview"], ["/ledger", "Contradiction Ledger"], ["/exits", "Exit Ledger"], ["/fields", "Field Audit"]] },
  { title: "Outlook", items: [["/warning", "Early Warning"], ["/predict", "Predictions"], ["/drivers", "Drivers & Benchmark"]] },
  { title: "About", items: [["/assistant", "Assistant"], ["/model-card", "Model Card"]] },
];

export function Layout() {
  const { bundle, error, sector, setSector } = useBundle();
  const cov = bundle?.findings.meta.coverage ?? [];
  const rows = cov.reduce((a, c) => a + c.rows_parsed, 0);
  const pcts = cov.filter((c) => c.pct != null).map((c) => c.pct as number);
  const avg = pcts.length ? pcts.reduce((a, b) => a + b, 0) / pcts.length : null;
  const sectors = bundle?.findings.by_sector.map((g) => g.key) ?? [];
  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 border-r border-line bg-surface px-3 py-4">
        <div className="mb-4 px-2 font-semibold tracking-tight">AGRIM</div>
        {GROUPS.map((g) => (
          <div key={g.title} className="mb-4">
            <div className="px-2 text-xs uppercase tracking-wide text-muted">{g.title}</div>
            {g.items.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === "/"}
                className={({ isActive }) => `block rounded px-2 py-1 text-sm ${isActive ? "bg-ground font-medium" : "text-ink hover:bg-ground"}`}>{label}</NavLink>
            ))}
          </div>
        ))}
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center gap-3 border-b border-line bg-surface px-4">
          <select className="rounded border border-line bg-surface px-2 py-1 text-sm" value={sector ?? ""} onChange={(e) => setSector(e.target.value || null)}>
            <option value="">IPMD · national view</option>
            {sectors.map((s) => <option key={s} value={s}>Ministry officer · {s}</option>)}
          </select>
          {bundle && (
            <span className="rounded border border-line px-2 py-1 text-xs text-muted">
              {cov.length} reports · <span className="num">{rows}</span> rows{avg != null ? <> · <span className="num">{avg.toFixed(1)}%</span> parsed</> : null}
            </span>
          )}
          <div className="flex-1" />
          {bundle && <ExportButton />}
        </header>
        <main className="mx-auto w-full max-w-[1440px] flex-1 p-4">
          {error && <div className="rounded border border-critical bg-surface p-4 text-critical">Data failed to load: {error}</div>}
          {!bundle && !error && <div className="p-6 text-muted">Loading the five reports…</div>}
          {bundle && <Outlet />}
        </main>
      </div>
    </div>
  );
}
