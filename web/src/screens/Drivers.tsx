import { useNavigate } from "react-router-dom";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, pct } from "../lib/format";

const FEAT: Record<string, string> = { log_cost_original: "log(original cost)", age_months: "months since approval", physical_progress_pct: "physical progress %" };

function Pdp({ target }: { target: string }) {
  const { bundle } = useBundle();
  const pd = bundle!.models!.m3_drivers.partial_dependence.filter((p) => p.target === target);
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 32 }, legend: { top: 0, textStyle: { fontSize: 10 } }, tooltip: { trigger: "axis" },
    xAxis: { type: "value", name: "feature value (each series on its own scale, normalised 0–1)" }, yAxis: { type: "value", name: target === "cost_overrun_pct" ? "expected overrun %" : "expected months" },
    series: pd.map((p) => { const lo = Math.min(...p.grid), hi = Math.max(...p.grid) || 1; return { name: FEAT[p.feature] ?? p.feature, type: "line" as const, showSymbol: false, data: p.grid.map((g, i) => [(g - lo) / (hi - lo || 1), p.values[i]]) }; }),
  }, [target]);
  return <div ref={ref} style={{ height: "260px" }} />;
}

export function Drivers() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const m = bundle!.models;
  if (!m) return <div className="rounded border border-line bg-surface p-6 text-muted">models.json is not present.</div>;
  const d = m.m3_drivers;
  const esc = bundle!.findings.escalation;
  const secRef = useEChart({
    grid: { left: "22%", right: 16, top: 16, bottom: 28 }, tooltip: {},
    yAxis: { type: "category", data: d.sector_effects.map((s) => s.sector) }, xAxis: { type: "value", name: "cost overrun effect (pct points, OLS)" },
    series: [{ type: "bar", data: d.sector_effects.map((s) => s.effect_cost_pct), color: "#1F5FA8" }],
  }, [d]);
  const pts = bundle!.projects.filter((p) => p.ml?.peer_expected_cost_overrun_pct != null).map((p) => {
    const last = p.snapshots[p.snapshots.length - 1];
    const actual = last.cost_original_cr && last.cost_revised_cr != null ? ((last.cost_revised_cr - last.cost_original_cr) / last.cost_original_cr) * 100 : null;
    return { code: p.project_code, x: p.ml!.peer_expected_cost_overrun_pct as number, y: actual };
  }).filter((p) => p.y != null);
  const lim = Math.max(1, ...pts.map((p) => Math.max(p.x, p.y as number)));
  const scRef = useEChart({
    grid: { left: 56, right: 16, top: 16, bottom: 36 },
    // Plan annotates this callback as (q: { data: number[] }); echarts declares it as
    // TopLevelFormatterParams, so the narrow annotation will not compile. Same runtime
    // behaviour, cast at the point of use.
    tooltip: { formatter: (q) => { const d = (q as unknown as { data: number[] }).data; return `expected ${d[0].toFixed(0)}% · actual ${d[1].toFixed(0)}%`; } },
    xAxis: { type: "value", name: "expected overrun % (peers)" }, yAxis: { type: "value", name: "actual overrun %" },
    series: [{ type: "scatter", symbolSize: 5, color: "#5B4B9A", data: pts.map((p) => [p.x, p.y, p.code]) }, { type: "line", data: [[0, 0], [lim, lim]], showSymbol: false, lineStyle: { type: "dashed" }, color: "#D5DCE4" }],
  }, [pts.length]);
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Drivers & Benchmark · what moves overrun across the panel</h1>
      <p className="max-w-3xl text-sm text-muted">Cross-sectional models on the {d.snapshot} report (n = <span className="num">{num(d.n)}</span>): ordinary least squares, the method of the published literature, beside gradient boosting. Five-fold cross-validation; this is a driver analysis, not a forecast.</p>
      <div className="overflow-x-auto rounded border border-line bg-surface"><table className="w-full text-sm">
        <thead><tr className="text-left text-xs uppercase text-muted"><th className="px-3 py-2">Target</th><th className="px-3 py-2">Model</th><th className="px-3 py-2">CV R²</th><th className="px-3 py-2">CV MAE</th></tr></thead>
        <tbody>{d.results.map((r, i) => <tr key={i} className="border-t border-line"><td className="px-3 py-2">{r.target === "cost_overrun_pct" ? "Cost overrun %" : "Time overrun (months)"}</td><td className="px-3 py-2">{r.model_id === "OLS" ? "OLS (conventional)" : "Gradient boosting"}</td><td className="num px-3 py-2">{r.cv_r2.toFixed(3)}</td><td className="num px-3 py-2">{r.cv_mae.toFixed(1)}</td></tr>)}</tbody></table></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Partial dependence · cost overrun %</div><Pdp target="cost_overrun_pct" /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Partial dependence · time overrun (months)</div><Pdp target="time_overrun_months" /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Sector effects (OLS coefficients)</div><div ref={secRef} style={{ height: "280px" }} /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Each project vs its peers (click a point in the table below to open)</div><div ref={scRef} style={{ height: "280px" }} /></div>
      </div>
      {/* Rule-based, no model. Counts only. No committee report number or date is cited: the
          attribution is unresolved, and the finding stands on the counts. */}
      <section className="rounded border border-line bg-surface p-3">
        <div className="mb-1 text-xs uppercase tracking-wide text-muted">Escalation matrix · rule-based</div>
        <p className="mb-2 max-w-3xl text-sm text-muted">
          A rollup is flagged when more than <span className="num">{pct(esc.threshold_pct, 0)}</span> of its
          classifiable projects are behind their stated schedule and that share is no better than it was
          in the first report parsed. Rollups with fewer than <span className="num">{num(esc.min_classifiable)}</span>{" "}
          classifiable projects keep their numbers here but are never flagged: a share over a handful of
          projects is not a rate.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase text-muted">
              <th className="py-1">Rollup</th>
              <th className="py-1 text-right font-normal">Classifiable</th>
              <th className="py-1 text-right font-normal">Behind schedule</th>
              <th className="py-1 text-right font-normal">Rate now</th>
              <th className="py-1 text-right font-normal">First report</th>
              <th className="py-1 text-right font-normal">Direction</th>
              <th className="py-1 text-right font-normal">Flagged</th>
            </tr></thead>
            <tbody>{esc.rows.map((r) => (
              <tr key={r.key} className="border-t border-line">
                <td className="py-1">{r.key}</td>
                <td className="num py-1 text-right">{num(r.classifiable)}</td>
                <td className="num py-1 text-right">{num(r.delayed)}</td>
                <td className="num py-1 text-right">{r.delay_rate_pct == null ? "—" : pct(r.delay_rate_pct)}</td>
                <td className="num py-1 text-right text-muted">{r.first_rate_pct == null ? "—" : pct(r.first_rate_pct)}</td>
                <td className="py-1 text-right">{r.improving == null ? <span className="text-muted">not comparable</span> : r.improving ? "improving" : "not improving"}</td>
                <td className="py-1 text-right">{r.escalate ? <span className="font-medium text-critical">flagged</span> : <span className="text-muted">no</span>}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          The rollup key is the agency string printed in the report, grouped. It is not a mapping to the
          official ministries, and one rollup may span several of them. &ldquo;Not comparable&rdquo; means the
          rollup had no classifiable projects in the first report parsed, so there is nothing to compare
          the current share with.
        </p>
      </section>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase text-muted">Worst residuals · overrun beyond what comparable projects show</div>
        <table className="w-full text-sm"><tbody>{bundle!.projects.filter((p) => p.ml?.cost_overrun_residual_pct != null).sort((a, b) => (b.ml!.cost_overrun_residual_pct as number) - (a.ml!.cost_overrun_residual_pct as number)).slice(0, 15).map((p) => (
          <tr key={p.project_code} className="cursor-pointer border-t border-line hover:bg-ground" onClick={() => nav(`/project/${p.project_code}`)}>
            <td className="num text-muted">{p.project_code}</td><td>{p.project_name}</td><td className="num text-right text-critical">+{(p.ml!.cost_overrun_residual_pct as number).toFixed(0)} pts</td></tr>))}</tbody></table>
      </div>
    </div>
  );
}
