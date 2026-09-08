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

// "Before" and "After" are not the same thing in every row. For EXP_DECREASE, PROG_DECREASE and
// STAT_ANOMALY they are one field read from two consecutive reports. For the rest — including
// EXP_GT_REVISED_COST, the largest type — they are two DIFFERENT fields read from the SAME report,
// and from_snapshot is null. Rendering both as an unlabelled Before → After showed a time series
// that is not there, and the shared "%" rule also printed a crore figure as a percentage. Each
// side now names its own field and its own unit.
type Unit = "cr" | "pct" | "text";
const SIDES: Record<string, [[string, Unit], [string, Unit]]> = {
  EXP_DECREASE: [["Expenditure, earlier report", "cr"], ["Expenditure, later report", "cr"]],
  PROG_DECREASE: [["Progress, earlier report", "pct"], ["Progress, later report", "pct"]],
  STAT_ANOMALY: [["Expenditure, earlier report", "cr"], ["Expenditure, later report", "cr"]],
  EXP_GT_REVISED_COST: [["Revised cost", "cr"], ["Cumulative expenditure", "cr"]],
  ZERO_PROG_NONZERO_EXP: [["Physical progress", "pct"], ["Cumulative expenditure", "cr"]],
  PROG_GT_100: [["—", "text"], ["Physical progress", "pct"]],
  DOC_BEFORE_APPROVAL: [["Approval month", "text"], ["Original completion date", "text"]],
};
const PAIRED = new Set(["EXP_DECREASE", "PROG_DECREASE", "STAT_ANOMALY"]);
const fmtUnit = (u: Unit, v: number | string | null) => (v == null ? "—" : typeof v === "number" ? (u === "pct" ? `${v}%` : u === "cr" ? crore(v) : String(v)) : v);
const Cell = ({ type, side, value }: { type: string; side: 0 | 1; value: number | string | null }) => {
  const spec = SIDES[type]?.[side];
  if (!spec) return <span className="num">{value == null ? "—" : String(value)}</span>;
  return <span className="block leading-tight"><span className="block text-[10px] uppercase text-muted">{spec[0]}</span><span className="num">{fmtUnit(spec[1], value)}</span></span>;
};

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
    { header: "Reports compared", accessorFn: (r) => (r.from_snapshot ? `${r.from_snapshot} → ${r.to_snapshot}` : r.to_snapshot),
      cell: (c) => <span className="num">{c.getValue() as string}{PAIRED.has(c.row.original.type) ? "" : <span className="ml-1 text-[10px] uppercase text-muted">within one report</span>}</span> },
    { header: "First value", accessorKey: "before", cell: (c) => <Cell type={c.row.original.type} side={0} value={c.getValue() as number | string | null} /> },
    { header: "Second value", accessorKey: "after", cell: (c) => <Cell type={c.row.original.type} side={1} value={c.getValue() as number | string | null} /> },
    { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> },
    { header: "Page", accessorFn: (r) => r.sources[r.sources.length - 1]?.page ?? null, cell: (c) => <span className="num">{String(c.getValue() ?? "—")}</span> },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Contradiction Ledger</h1>
      <p className="max-w-3xl text-sm text-muted">Each row is a statement in the Ministry's own report that cannot be true alongside another statement in the same or the previous report. Every row carries the page it was read from. Some types compare one field across two consecutive reports; others compare two different fields inside a single report — each row's two value columns say which fields they are.</p>
      <p className="max-w-3xl text-xs text-muted">Statistical outliers are model output (M4 isolation forest), listed here for convenience and excluded from the arithmetic-contradiction total on the Overview.</p>
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
