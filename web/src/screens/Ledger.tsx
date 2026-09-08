import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { crore, sevClass } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["contradictions"]["rows"][number];
const ORDER = ["EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL", "STAT_ANOMALY"];
const LABEL: Record<string, string> = { EXP_DECREASE: "Cumulative expenditure fell", PROG_DECREASE: "Progress fell", EXP_GT_REVISED_COST: "Spent more than revised cost",
  ZERO_PROG_NONZERO_EXP: "0% progress, money spent", PROG_GT_100: "Progress above 100%", DOC_BEFORE_APPROVAL: "Completion before approval", STAT_ANOMALY: "Statistical outlier (model)" };

const fmt = (t: string, v: number | string | null) => (v == null ? "—" : typeof v === "number" ? (t === "PROG_DECREASE" || t === "PROG_GT_100" || t === "ZERO_PROG_NONZERO_EXP" ? `${v}%` : crore(v)) : v);

export function Ledger() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const type = params.get("type") ?? "";
  const counts = new Map(bundle!.findings.contradictions.by_type.map((t) => [t.type, t.count]));
  const rows = useMemo(() => bundle!.findings.contradictions.rows.filter((r) => (!type || r.type === type) &&
    (!sector || bundle!.byCode.get(r.project_code)?.sector === sector)), [bundle, type, sector]);
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Type", accessorKey: "type", cell: (c) => LABEL[c.getValue() as string] ?? (c.getValue() as string) },
    { header: "Months", accessorFn: (r) => `${r.from_snapshot ?? ""} → ${r.to_snapshot}`, cell: (c) => <span className="num">{c.getValue() as string}</span> },
    { header: "Before", accessorKey: "before", cell: (c) => <span className="num">{fmt(c.row.original.type, c.getValue() as number | string | null)}</span> },
    { header: "After", accessorKey: "after", cell: (c) => <span className="num">{fmt(c.row.original.type, c.getValue() as number | string | null)}</span> },
    { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> },
    { header: "Page", accessorFn: (r) => r.sources[r.sources.length - 1]?.page ?? null, cell: (c) => <span className="num">{String(c.getValue() ?? "—")}</span> },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Contradiction Ledger</h1>
      <p className="max-w-3xl text-sm text-muted">Each row is a statement in the Ministry's own report that cannot be true alongside another statement in the same or the previous report. Every row carries the page it was read from.</p>
      <div className="flex flex-wrap gap-2">
        <button onClick={() => setParams({})} className={`rounded border px-2 py-1 text-xs ${!type ? "border-accent bg-ground" : "border-line"}`}>All · {bundle!.findings.contradictions.rows.length}</button>
        {ORDER.filter((t) => counts.has(t)).map((t) => (
          <button key={t} onClick={() => setParams({ type: t })} className={`rounded border px-2 py-1 text-xs ${type === t ? "border-accent bg-ground" : "border-line"}`}>{LABEL[t]} · {counts.get(t)}</button>
        ))}
      </div>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="680px" />
    </div>
  );
}
