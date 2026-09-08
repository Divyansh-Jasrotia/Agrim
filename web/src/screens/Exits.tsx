import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { crore, num, pct } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["exits"]["rows"][number];
const PART: Record<string, string> = { LAST_SEEN_GE_95: "≥95% when last seen", LAST_SEEN_50_95: "50–95% when last seen", LAST_SEEN_LT_50: "<50% when last seen", UNKNOWN: "progress not printed" };

export function Exits() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const ex = bundle!.findings.exits;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 28 }, legend: { top: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: ex.pairs.map((p) => `${p.from} → ${p.to}`) }, yAxis: { type: "value", name: "projects" },
    series: [
      { name: "left the panel", type: "bar", data: ex.pairs.map((p) => p.exited), color: "#B42318" },
      { name: "entered", type: "bar", data: ex.pairs.map((p) => p.entered), color: "#1E7B4F" },
      // Null means the report did not print a commissioned count for that window. ECharts leaves a gap
      // for null; rendering 0 would state that nothing was commissioned, which the report never says.
      { name: "commissioned (printed)", type: "bar", data: ex.pairs.map((p) => p.commissioned_printed ?? null), color: "#4B5A6B" },
    ],
  }, [ex]);
  const parts = new Map<string, number>();
  ex.rows.forEach((r) => parts.set(r.partition, (parts.get(r.partition) ?? 0) + 1));
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Last seen", accessorKey: "last_seen", cell: (c) => <span className="num">{c.getValue() as string}</span> },
    { header: "Progress", accessorKey: "last_progress_pct", cell: (c) => <span className="num">{pct(c.getValue() as number | null)}</span> },
    { header: "Expenditure", accessorKey: "last_expenditure_cr", cell: (c) => <span className="num">{crore(c.getValue() as number | null)}</span> },
    { header: "Revised cost", accessorKey: "last_cost_revised_cr", cell: (c) => <span className="num">{crore(c.getValue() as number | null)}</span> },
    { header: "State when last seen", accessorKey: "partition", cell: (c) => PART[c.getValue() as string] },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Exit Ledger</h1>
      <p className="max-w-3xl text-sm text-muted">Projects present in one report and absent from the next. These are net changes in the published panel; the reason a project leaves (commissioned, re-scoped, transferred, dropped) is a status field behind login, so rows are labelled by their last observed state, never as cancelled.</p>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "260px" }} /></div>
      <div className="flex flex-wrap gap-2 text-sm">{[...parts.entries()].map(([k, v]) => <span key={k} className="rounded border border-line bg-surface px-2 py-1">{PART[k]} · <span className="num">{num(v)}</span></span>)}
        {/* This sum is total revised COST, not overrun. Labelling it "overrun" put a figure several times
            the whole panel's recorded overrun on the screen; the parenthetical did not undo the headline. */}
        <span className="rounded border border-line bg-surface px-2 py-1">revised cost of the rows that left: <span className="num">{crore(ex.pairs.reduce((a, p) => a + p.exited_cost_revised_cr, 0))}</span></span></div>
      <DataTable columns={columns} rows={ex.rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="520px" />
    </div>
  );
}
