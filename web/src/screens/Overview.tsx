import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { IndiaMap } from "../components/IndiaMap";
import { KPI } from "../components/KPI";
import { useBundle } from "../data/store";
import { bandClass, crore, num, pct, share } from "../lib/format";
import type { Project } from "../types/projects";

export function Overview() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const h = bundle!.findings.meta.headline;
  const latest = bundle!.findings.meta.snapshots[bundle!.findings.meta.snapshots.length - 1];
  // h.contradictions_total counts the rule-based arithmetic contradictions only. STAT_ANOMALY rows
  // are M4 isolation-forest output and get their own tile: the ledger shows both, the headline
  // never adds them together. Both numbers come from the bundle, neither is typed in.
  const modelOutliers = bundle!.findings.contradictions.by_type.find((t) => t.type === "STAT_ANOMALY")?.count ?? null;
  const rows = useMemo(() => bundle!.projects
    .filter((p) => p.status === "ongoing" && (!sector || p.sector === sector))
    .sort((a, b) => b.risk.score - a.risk.score || (b.ml?.slip_prob ?? 0) - (a.ml?.slip_prob ?? 0))
    .slice(0, 20), [bundle, sector]);
  const columns: ColumnDef<Project, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "State", accessorKey: "state" },
    { header: "Progress", accessorFn: (p) => p.snapshots[p.snapshots.length - 1].physical_progress_pct, cell: (c) => <span className="num">{pct(c.getValue() as number | null)}</span> },
    { header: "Rule risk", accessorFn: (p) => p.risk.score, cell: (c) => <Badge text={`${c.row.original.risk.band} · ${num(c.getValue() as number)}`} className={bandClass[c.row.original.risk.band]} /> },
    { header: "Slip prob. (model)", accessorFn: (p) => p.ml?.slip_prob ?? null, cell: (c) => <span className="num text-model">{share(c.getValue() as number | null)}</span> },
  ];
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8">
        <KPI label={`Projects · ${latest}`} value={num(h.projects_latest)} />
        <KPI label="Revised cost" value={crore(h.cost_revised_total_cr)} />
        <KPI label="Recorded overrun" value={crore(h.overrun_total_cr)} hint="revised minus original" />
        <KPI label="Arithmetic contradictions" value={num(h.contradictions_total)} hint="rule-based, across all reports parsed" />
        <KPI label="Left the panel" value={num(h.exits_total)} />
        <KPI label="Unreachable dates" value={num(h.unreachable_total)} hint="at own reported pace" />
        <KPI label="Statistical outliers" value={num(modelOutliers)} hint="isolation forest, not arithmetic" model />
        <KPI label="Watchlist" value={num(h.watchlist_size)} model />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Flagged projects by state</div><IndiaMap /></div>
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 text-xs uppercase text-muted">By sector</div>
          <table className="w-full"><tbody>{bundle!.findings.by_sector.slice().sort((a, b) => b.flagged - a.flagged).map((g) => <tr key={g.key} className="border-t border-line"><td>{g.key}</td><td className="num text-right">{num(g.flagged)} / {num(g.projects)} flagged</td><td className="num text-right text-critical">{num(g.red)} red</td></tr>)}</tbody></table>
        </div>
      </div>
      <h2 className="text-lg font-semibold">Top 20 by rule-based risk{sector ? ` · ${sector}` : ""}</h2>
      <DataTable columns={columns} rows={rows} onRowClick={(p) => nav(`/project/${p.project_code}`)} height="720px" />
    </div>
  );
}
