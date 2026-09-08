import { useParams } from "react-router-dom";
import { Badge } from "../components/Badge";
import { SourcePage } from "../components/SourcePage";
import { Sparkline } from "../components/Sparkline";
import { useBundle } from "../data/store";
import { bandClass, crore, monthLabel, num, pct, sevClass, share } from "../lib/format";

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
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Physical progress</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.physical_progress_pct)} forecast={ml?.progress_next_pred ?? null} color="#1F5FA8" unit="%" />
        </div>
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Cumulative expenditure (₹ cr)</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.expenditure_cum_cr)} color="#1E7B4F" unit="₹ cr" />
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
                <span>{f.detail} {f.sources.map((s) => <SourcePage key={`${s.snapshot}-${s.page}`} snapshot={s.snapshot} page={s.page} />)}</span>
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
              <ul className="space-y-1">
                {ml.slip_top_factors.map((f) => (
                  <li key={f.feature} className="flex items-center gap-2">
                    <span className="w-44 truncate text-muted" title={f.feature}>{f.feature}</span>
                    <span className="h-2 rounded bg-model" style={{ width: `${Math.min(96, Math.abs(f.contribution) * 60)}px`, opacity: f.contribution >= 0 ? 1 : 0.4 }} />
                    <span className="num text-xs">{f.contribution >= 0 ? "+" : ""}{f.contribution.toFixed(2)} · {f.value == null ? "—" : typeof f.value === "number" ? f.value.toFixed(1) : f.value}</span>
                  </li>
                ))}
              </ul>
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
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-muted">Brief {brief && <Badge text={`LLM · ${brief.model} · ${brief.grounded ? "verified against ledger" : "template fallback"}`} className="bg-line text-muted" />}</div>
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
