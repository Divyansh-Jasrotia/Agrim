import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { bandClass, num, share } from "../lib/format";

const NAME: Record<string, string> = { LR_A: "Logistic regression · set A (conventional)", HGB_A: "Gradient boosting · set A", HGB_B: "Gradient boosting · set B (+ audit features)", HGB_B_SHUFFLED: "Control: labels shuffled" };
const COLOR: Record<string, string> = { LR_A: "#4B5A6B", HGB_A: "#8DA6C7", HGB_B: "#5B4B9A", HGB_B_SHUFFLED: "#D5DCE4" };

interface WRow { code: string; name: string; prob: number; rank: number; factor: string; band: string; delay: number | null; page: number }

export function Predict() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const m = bundle!.models;
  if (!m) return <div className="rounded border border-line bg-surface p-6 text-muted">models.json is not present. Run findings/run.py without --no-models.</div>;
  const test = m.meta.test_pair;
  const res = m.m1_slip.results.filter((r) => r.test_pair === test);
  const pair = m.meta.pairs.find((p) => p.id === test);
  const prRef = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 32 }, legend: { top: 0, textStyle: { fontSize: 10 } }, tooltip: { trigger: "item" },
    xAxis: { type: "value", name: "recall", min: 0, max: 1 }, yAxis: { type: "value", name: "precision", min: 0, max: 1 },
    series: res.map((r) => ({ name: NAME[r.model_id] ?? r.model_id, type: "line" as const, showSymbol: false, color: COLOR[r.model_id], data: r.pr_curve.map((p) => [p.x, p.y]) })),
  }, [test]);
  const hb = res.find((r) => r.model_id === "HGB_B");
  const calRef = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 32 }, tooltip: {},
    xAxis: { type: "value", name: "predicted", min: 0, max: 1 }, yAxis: { type: "value", name: "observed", min: 0, max: 1 },
    series: [{ type: "line", data: [[0, 0], [1, 1]], lineStyle: { type: "dashed" }, color: "#D5DCE4", showSymbol: false },
      { type: "scatter", color: "#5B4B9A", data: (hb?.calibration ?? []).filter((c) => c.mean_pred != null).map((c) => [c.mean_pred, c.mean_obs, c.n]), symbolSize: (d: number[]) => Math.min(30, 4 + Math.sqrt(d[2])) }],
  }, [test]);
  const rows: WRow[] = m.m1_slip.watchlist.map((w) => {
    const p = bundle!.byCode.get(w.project_code)!;
    return { code: w.project_code, name: p.project_name, prob: w.slip_prob, rank: w.slip_rank, factor: p.ml?.slip_top_factors[0]?.feature ?? "—", band: p.risk.band,
      delay: p.ml?.expected_delay_months ?? null, page: p.snapshots[p.snapshots.length - 1].page };
  });
  const columns: ColumnDef<WRow, unknown>[] = [
    { header: "Rank", accessorKey: "rank", cell: (c) => <span className="num">{c.getValue() as number}</span> },
    { header: "Project", accessorKey: "name", cell: (c) => <span><span className="num text-muted">{c.row.original.code}</span> {c.getValue() as string}</span> },
    { header: "Slip prob. (model)", accessorKey: "prob", cell: (c) => <span className="num text-model">{share(c.getValue() as number)}</span> },
    { header: "Top factor", accessorKey: "factor" },
    { header: "Rule band", accessorKey: "band", cell: (c) => <Badge text={c.getValue() as string} className={bandClass[c.getValue() as string]} /> },
    { header: "Expected delay (months)", accessorKey: "delay", cell: (c) => <span className="num">{c.getValue() == null ? "—" : num(c.getValue() as number)}</span> },
    { header: "Page", accessorKey: "page", cell: (c) => <span className="num">{c.getValue() as number}</span> },
  ];
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Predictions · will a revised completion date be filed next report?</h1>
      <p className="max-w-3xl text-sm text-muted">Trained on {m.meta.train_pairs.join(", ")}, tested on {test} ({pair?.from} → {pair?.to}), a report the models never saw. n = <span className="num">{num(pair?.n)}</span>, projects that filed = <span className="num">{num(pair?.positives)}</span>, exits excluded = <span className="num">{num(pair?.censored_exits)}</span>. The conventional method is shown even where it wins.</p>
      <div className="overflow-x-auto rounded border border-line bg-surface">
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase text-muted"><th className="px-3 py-2">Model</th><th className="px-3 py-2">PR-AUC</th><th className="px-3 py-2">ROC-AUC</th><th className="px-3 py-2">Precision@100</th><th className="px-3 py-2">Recall@100</th><th className="px-3 py-2">Lift@100</th></tr></thead>
          <tbody>{res.map((r) => <tr key={r.model_id} className="border-t border-line" style={{ color: r.model_id === "HGB_B_SHUFFLED" ? "#4B5A6B" : undefined }}>
            <td className="px-3 py-2">{NAME[r.model_id] ?? r.model_id}</td><td className="num px-3 py-2">{r.pr_auc.toFixed(3)}</td><td className="num px-3 py-2">{r.roc_auc == null ? "—" : r.roc_auc.toFixed(3)}</td>
            <td className="num px-3 py-2">{share(r.precision_at_100)}</td><td className="num px-3 py-2">{share(r.recall_at_100)}</td><td className="num px-3 py-2">{r.lift_at_100 == null ? "—" : `${r.lift_at_100.toFixed(1)}×`}</td></tr>)}</tbody>
        </table>
        <div className="px-3 py-2 text-xs text-muted">Base rate on the test pair: {share(res[0]?.base_rate)}. Set B adds audit-derived features (pace, unreachable ratio, prior filings, agency history); the difference between the two gradient-boosting rows is the part of predictive power not on the current form.</div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Precision–recall on the held-out pair</div><div ref={prRef} style={{ height: "280px" }} /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Calibration (gradient boosting, set B)</div><div ref={calRef} style={{ height: "280px" }} /></div>
      </div>
      <h2 className="text-lg font-semibold">Watchlist · the 100 projects to review this month</h2>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.code}`)} height="600px" />
    </div>
  );
}
