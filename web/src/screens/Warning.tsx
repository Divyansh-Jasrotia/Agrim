import type { ColumnDef } from "@tanstack/react-table";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, pct, sevClass } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["early_warning"]["rows"][number];
type DelayRow = Findings["delay_series"]["rows"][number];
// The band edges the April 2014 report itself printed.
const BANDS: { key: keyof DelayRow & ("on_schedule" | "d_1_12" | "d_13_24" | "d_25_60" | "d_61_plus"); label: string }[] = [
  { key: "on_schedule", label: "On schedule" },
  { key: "d_1_12", label: "1–12 mo" },
  { key: "d_13_24", label: "13–24 mo" },
  { key: "d_25_60", label: "25–60 mo" },
  { key: "d_61_plus", label: "61+ mo" },
];

export function Warning() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const [tab, setTab] = useState<"unreachable" | "passed">("unreachable");
  const ds = bundle!.findings.delay_series;
  const all = bundle!.findings.early_warning.rows.filter((r) => !sector || bundle!.byCode.get(r.project_code)?.sector === sector);
  // These rows carry two different findings. months_remaining <= 0 is the DOC_PASSED case: the date
  // the project states is already behind us. months_remaining > 0 is DOC_UNREACHABLE: the date is
  // ahead but the project's own pace does not get there. The Overview KPI counts only the second,
  // so listing all of them under one heading put two different numbers on two screens.
  const passed = all.filter((r) => r.months_remaining <= 0);
  const unreachable = all.filter((r) => r.months_remaining > 0);
  const rows = tab === "unreachable" ? unreachable : passed;
  const edges = [1, 1.25, 1.5, 2, 3, 5, 10];
  const bins = edges.map((e, i) => unreachable.filter((r) => r.ratio != null && r.ratio >= e && (i === edges.length - 1 || (r.ratio as number) < edges[i + 1])).length);
  const noPace = unreachable.filter((r) => r.ratio == null).length;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 44 }, tooltip: {},
    xAxis: { type: "category", axisLabel: { interval: 0, fontSize: 10 }, data: [...edges.map((e, i) => (i === edges.length - 1 ? `≥${e}×` : `${e}–${edges[i + 1]}×`)), "no usable pace"] },
    yAxis: { type: "value", name: "projects" },
    series: [{ type: "bar", data: [...bins, noPace], color: "#C2410C" }],
  }, [unreachable.length]);

  const project: ColumnDef<Row, unknown> = { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> };
  const pace: ColumnDef<Row, unknown> = { header: "Pace (pt/month)", accessorKey: "velocity_pct_per_month", cell: (c) => <span className="num">{c.getValue() == null ? "—" : (c.getValue() as number).toFixed(2)}</span> };
  const severity: ColumnDef<Row, unknown> = { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> };

  const unreachableCols: ColumnDef<Row, unknown>[] = [
    project, pace,
    // A null months_needed is not "infinity". It is a pace that is flat, negative, or so slow that
    // the projection runs past the horizon the pipeline is willing to state — say that instead.
    { header: "Months needed", accessorKey: "months_needed", cell: (c) => (c.getValue() == null ? <span className="text-muted">no date at this pace</span> : <span className="num">{num(c.getValue() as number)}</span>) },
    { header: "Months left", accessorKey: "months_remaining", cell: (c) => <span className="num">{num(c.getValue() as number)}</span> },
    { header: "Ratio", accessorKey: "ratio", cell: (c) => (c.getValue() == null ? <span className="text-muted">—</span> : <span className="num">{`${(c.getValue() as number).toFixed(1)}×`}</span>) },
    severity,
  ];
  const passedCols: ColumnDef<Row, unknown>[] = [
    project, pace,
    // months_remaining is negative here by construction; print the sign as the word it means
    // rather than showing "-7" under a column headed "Months left".
    { header: "Months past its stated date", accessorFn: (r) => -r.months_remaining, cell: (c) => <span className="num">{num(c.getValue() as number)} overdue</span> },
    severity,
  ];

  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Early Warning · completion dates the reports do not support</h1>
      <p className="max-w-3xl text-sm text-muted">No model. Two separate findings, kept apart because they say different things: a date that is still ahead but out of reach at the project's own reported pace, and a date that has already gone by. A ratio of 2× means the project needs twice the time it says it has left.</p>
      <div className="flex flex-wrap gap-2">
        <button onClick={() => setTab("unreachable")} className={`rounded border px-2 py-1 text-xs ${tab === "unreachable" ? "border-accent bg-ground" : "border-line"}`}>Unreachable at its own pace · {num(unreachable.length)}</button>
        <button onClick={() => setTab("passed")} className={`rounded border px-2 py-1 text-xs ${tab === "passed" ? "border-accent bg-ground" : "border-line"}`}>Stated date already passed · {num(passed.length)}</button>
      </div>
      {tab === "unreachable" ? (
        <>
          <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "220px" }} /></div>
          <p className="max-w-3xl text-xs text-muted">"No usable pace" is a project whose reported progress is flat, has moved backwards, or is so slow that a completion month would land beyond the horizon this pipeline is willing to state. The finding stands; no month is projected for it.</p>
        </>
      ) : (
        <p className="max-w-3xl text-xs text-muted">These projects report less than 100% progress against a completion date that is already in the past. The pace column is what they reported over the months observed; no ratio is computed, because there is no remaining time to compare it with.</p>
      )}
      {/* The delay bands the Flash Reports used to publish, recomputed from the fields they still
          publish. A continuity-of-series reconstruction, not an accusation. */}
      <section className="rounded border border-line bg-surface p-3">
        <div className="text-xs uppercase tracking-wide text-muted">Delay bands, reconstructed</div>
        <p className="mt-1 max-w-3xl text-sm text-muted">
          Earlier Flash Reports printed how many projects were behind schedule, in these bands. Later
          reports stopped. These counts are recomputed from the completion dates the reports still
          print, so the series continues. Projects with no original date are excluded and counted
          separately rather than assumed to be on schedule.
        </p>
        <table className="mt-2 w-full text-sm">
          <thead><tr className="text-left text-xs uppercase text-muted">
            <th className="py-1">Report</th>
            {BANDS.map((b) => <th key={b.key} className="py-1 text-right font-normal">{b.label}</th>)}
            <th className="py-1 text-right font-normal">Classifiable</th>
            <th className="py-1 text-right font-normal">No original date</th>
          </tr></thead>
          <tbody>
            {ds.rows.map((r) => (
              <tr key={r.snapshot} className="border-t border-line">
                <td className="num py-1">{r.snapshot}</td>
                {BANDS.map((b) => (
                  <td key={b.key} className="num py-1 text-right">
                    {num(r[b.key])}
                    <span className="ml-1 text-xs text-muted">{r.classifiable ? pct((r[b.key] / r.classifiable) * 100, 0) : "—"}</span>
                  </td>
                ))}
                <td className="num py-1 text-right">{num(r.classifiable)}</td>
                <td className="num py-1 text-right text-muted">{num(r.doc_null)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <DataTable columns={tab === "unreachable" ? unreachableCols : passedCols} rows={rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="560px" />
    </div>
  );
}
