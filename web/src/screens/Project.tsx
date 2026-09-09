import { useParams } from "react-router-dom";
import { Badge } from "../components/Badge";
import { Caveat } from "../components/Caveat";
import { ShapBars } from "../components/ShapBars";
import { SourcePage } from "../components/SourcePage";
import { Sparkline } from "../components/Sparkline";
import { useBundle } from "../data/store";
import { bandClass, crore, monthLabel, num, pct, sevClass, share } from "../lib/format";

// Worst first. Matches the severity enum in the contract.
const SEVERITY = ["critical", "high", "medium", "low", "info"];

export function Project() {
  const { code } = useParams();
  const { bundle } = useBundle();
  const p = code ? bundle!.byCode.get(code) : undefined;
  if (!p) return <div className="text-muted">No project with code {code}.</div>;
  const last = p.snapshots[p.snapshots.length - 1];
  const prev = p.snapshots.length > 1 ? p.snapshots[p.snapshots.length - 2] : null;
  const labels = p.snapshots.map((s) => s.snapshot);
  const brief = bundle!.briefs?.find((b) => b.project_code === p.project_code) ?? null;
  const ml = p.ml;
  // The one thing the eye should land on: the worst flag, promoted above everything else.
  // Rank by severity, ties broken by the earliest report the condition appeared in.
  const worst = p.flags.length
    ? p.flags.slice().sort((a, b) =>
        (SEVERITY.indexOf(a.severity) - SEVERITY.indexOf(b.severity))
        || String(a.first_snapshot ?? a.to_snapshot).localeCompare(String(b.first_snapshot ?? b.to_snapshot)))[0]
    : null;
  const alertsFor = (types: string[]) =>
    p.flags.filter((f) => types.includes(f.type)).flatMap((f) => f.sources.map((x) => x.snapshot));
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="num text-sm text-muted">{p.project_code}{p.agency_raw ? ` · ${p.agency_raw}` : ""}{p.state ? ` · ${p.state}` : ""}{p.sector ? ` · ${p.sector}` : ""}</div>
          <h1 className="text-xl font-semibold">{p.project_name}</h1>
          <div className="text-sm text-muted">Seen {p.first_seen} → {p.last_seen} · {p.status === "exited" ? "left the monitored panel" : "ongoing"} · stated completion {monthLabel(last.doc_revised ?? last.doc_original)}{last.doc_revised ? ` (revised from ${monthLabel(last.doc_original)})` : ""}</div>
        </div>
        <div className="flex items-center gap-2">
          <Badge text={`${p.risk.band} · rule score ${num(p.risk.score)}`} className={bandClass[p.risk.band]} />
          <SourcePage snapshot={last.snapshot} page={last.page} />
        </div>
      </div>
      {/* The evidence, full width, above everything. One focal point, not six equal cards.
          Both source pages are the real rendered pages, shown side by side. */}
      {worst && (
        <section className="rounded border border-critical bg-surface p-4">
          <div className="flex items-baseline gap-2">
            <Badge text={worst.severity} className={sevClass[worst.severity]} />
            <span className="num text-xs text-muted">
              {worst.type}
              {(worst.occurrences ?? 1) > 1 && <> · {worst.first_snapshot ?? worst.to_snapshot} → {worst.to_snapshot} · {worst.occurrences} reports</>}
            </span>
          </div>
          <p className="mt-2 max-w-4xl text-xl leading-snug">{worst.detail}</p>
          <div className="mt-2"><Caveat /></div>
          {worst.sources.length > 0 && (
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {worst.sources.slice(0, 2).map((x) => (
                <SourcePage key={`${x.snapshot}-${x.page}`} snapshot={x.snapshot} page={x.page} inline />
              ))}
            </div>
          )}
          {worst.sources.length > 2 && (
            <p className="mt-2 text-xs text-muted">
              Also printed on {worst.sources.slice(2).map((x) => `${x.snapshot} p.${x.page}`).join(", ")}.
            </p>
          )}
        </section>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Physical progress</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.physical_progress_pct)} forecast={ml?.progress_next_pred ?? null} unit="%" alertLabels={alertsFor(["PROG_DECREASE", "PROG_GT_100"])} />
        </div>
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Cumulative expenditure (₹ cr)</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.expenditure_cum_cr)} unit="₹ cr" alertLabels={alertsFor(["EXP_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP"])} />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="mb-2 text-xs uppercase tracking-wide text-muted">Flags · {p.flags.length}</div>
          {p.flags.length === 0 && <div className="text-sm text-muted">No flags. The record is internally consistent across the reports we parsed.</div>}
          <ul className="space-y-2">
            {p.flags.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <Badge text={f.severity} className={sevClass[f.severity]} />
                <span>
                  {f.detail}
                  {/* One persisting condition is one row. The month range and every page it was
                      printed on are shown, so collapsing never hides a citation. */}
                  {(f.occurrences ?? 1) > 1 && (
                    <span className="num ml-1 text-xs text-muted">
                      {f.first_snapshot ?? f.to_snapshot} → {f.to_snapshot} · {f.occurrences} reports
                    </span>
                  )}{" "}
                  {f.sources.map((s) => <SourcePage key={`${s.snapshot}-${s.page}`} snapshot={s.snapshot} page={s.page} />)}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className={`rounded border bg-surface p-3 ${ml ? "border-model" : "border-line"}`}>
          <div className="mb-2 text-xs uppercase tracking-wide text-model">Outlook · model</div>
          {!ml && <div className="text-sm text-muted">No model score for this project (exited, or models not run).</div>}
          {ml && (
            <div className="space-y-2 text-sm">
              <div>Chance a revised completion date is filed next report: <span className="num font-medium text-model">{share(ml.slip_prob)}</span>{ml.slip_rank != null && <span className="text-muted"> · rank {ml.slip_rank}</span>}</div>
              <ShapBars factors={ml.slip_top_factors} />
              <div>Expected completion at the winning method's pace: <span className="num">{monthLabel(ml.expected_completion)}</span>{ml.expected_delay_months != null && <span> · <span className={`num ${ml.expected_delay_months > 0 ? "text-critical" : "text-ok"}`}>{ml.expected_delay_months > 0 ? "+" : ""}{num(ml.expected_delay_months)} months</span> vs stated date</span>}</div>
              {ml.cost_overrun_residual_pct != null && <div>Cost overrun vs comparable projects: <span className={`num ${ml.cost_overrun_residual_pct > 0 ? "text-critical" : "text-ok"}`}>{ml.cost_overrun_residual_pct > 0 ? "+" : ""}{pct(ml.cost_overrun_residual_pct)}</span> (peers expected {pct(ml.peer_expected_cost_overrun_pct)})</div>}
              {ml.anomaly_flag && <div className="text-muted">Flagged as a statistical outlier by the anomaly model.</div>}
            </div>
          )}
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 text-xs uppercase tracking-wide text-muted">Assistant · this project</div>
          <details open><summary className="cursor-pointer">Why is {p.project_code} rated {p.risk.band}?</summary>
            <ul className="mt-1 list-disc pl-5">{p.risk.reasons.length ? p.risk.reasons.map((r, i) => <li key={i}>{r}</li>) : <li>No contributing flags.</li>}</ul></details>
          <details><summary className="cursor-pointer">What changed between {prev?.snapshot ?? "—"} and {last.snapshot}?</summary>
            {prev ? <ul className="mt-1 list-disc pl-5">
              <li>Progress {pct(prev.physical_progress_pct)} → {pct(last.physical_progress_pct)}</li>
              <li>Expenditure {crore(prev.expenditure_cum_cr)} → {crore(last.expenditure_cum_cr)}</li>
              <li>Revised cost {crore(prev.cost_revised_cr)} → {crore(last.cost_revised_cr)}</li>
              <li>Revised date {monthLabel(prev.doc_revised)} → {monthLabel(last.doc_revised)}</li>
            </ul> : <div className="text-muted">Only one report has this project.</div>}</details>
        </div>
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-muted">Brief {brief && <Badge text={`${brief.model === "template" ? "Template" : `LLM · ${brief.model}`} · ${brief.grounded ? "verified against ledger" : "not verified"}`} className="bg-line text-muted" />}</div>
          {brief ? <p>{brief.brief}</p> : <p className="text-muted">No cached brief for this project.</p>}
        </div>
      </div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">As printed, by report</div>
        <table className="w-full text-sm"><thead><tr className="text-left text-xs uppercase text-muted"><th>Report</th><th>Page</th><th>Original DoC</th><th>Revised DoC</th><th>Original cost</th><th>Revised cost</th><th>Expenditure</th><th>Progress</th></tr></thead>
          <tbody>{p.snapshots.map((s) => <tr key={s.snapshot} className="border-t border-line"><td className="num">{s.snapshot}</td><td className="num">{s.page}</td><td>{monthLabel(s.doc_original)}</td><td>{monthLabel(s.doc_revised)}</td><td className="num">{crore(s.cost_original_cr)}</td><td className="num">{crore(s.cost_revised_cr)}</td><td className="num">{crore(s.expenditure_cum_cr)}</td><td className="num">{pct(s.physical_progress_pct)}</td></tr>)}</tbody></table>
      </div>
    </div>
  );
}
