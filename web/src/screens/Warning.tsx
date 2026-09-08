import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, sevClass } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["early_warning"]["rows"][number];

export function Warning() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const rows = bundle!.findings.early_warning.rows.filter((r) => !sector || bundle!.byCode.get(r.project_code)?.sector === sector);
  const edges = [1, 1.25, 1.5, 2, 3, 5, 10];
  const bins = edges.map((e, i) => rows.filter((r) => r.ratio != null && r.ratio >= e && (i === edges.length - 1 || (r.ratio as number) < edges[i + 1])).length);
  const stalled = rows.filter((r) => r.ratio == null).length;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 28 }, tooltip: {},
    xAxis: { type: "category", data: [...edges.map((e, i) => (i === edges.length - 1 ? `≥${e}×` : `${e}–${edges[i + 1]}×`)), "no progress"] },
    yAxis: { type: "value", name: "projects" },
    series: [{ type: "bar", data: [...bins, stalled], color: "#C2410C" }],
  }, [rows.length]);
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Pace (pt/month)", accessorKey: "velocity_pct_per_month", cell: (c) => <span className="num">{c.getValue() == null ? "—" : (c.getValue() as number).toFixed(2)}</span> },
    { header: "Months needed", accessorKey: "months_needed", cell: (c) => <span className="num">{c.getValue() == null ? "∞" : num(c.getValue() as number)}</span> },
    { header: "Months left", accessorKey: "months_remaining", cell: (c) => <span className="num">{num(c.getValue() as number)}</span> },
    { header: "Ratio", accessorKey: "ratio", cell: (c) => <span className="num">{c.getValue() == null ? "—" : `${(c.getValue() as number).toFixed(1)}×`}</span> },
    { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Early Warning · unreachable completion dates</h1>
      <p className="max-w-3xl text-sm text-muted">No model. For each project, the progress rate it reports itself is compared with the months left to the date it states itself. A ratio of 2× means it needs twice the time it says it has.</p>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "220px" }} /></div>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="560px" />
    </div>
  );
}
