import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { Caveat } from "../components/Caveat";
import { CsvButton } from "../components/CsvButton";
import { DataTable } from "../components/DataTable";
import { IndiaMap } from "../components/IndiaMap";
import { KPI } from "../components/KPI";
import { useBundle } from "../data/store";
import { bandClass, crore, croreShort, monthLabel, num, pct, share } from "../lib/format";
import type { Project } from "../types/projects";

const TOP_N = 20;

export function Overview() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const h = bundle!.findings.meta.headline;
  const snaps = bundle!.findings.meta.snapshots;
  const latest = snaps[snaps.length - 1];
  // Every figure below comes from the bundle. contradictions_arithmetic counts rule-based
  // arithmetic contradictions only; STAT_ANOMALY rows are M4 isolation-forest output and get
  // their own tile and their own bar. The headline never adds the two together.
  const byType = bundle!.findings.contradictions.by_type;
  const arithmetic = byType.filter((t) => t.type !== "STAT_ANOMALY").slice().sort((a, b) => b.count - a.count);
  const anomalies = byType.find((t) => t.type === "STAT_ANOMALY") ?? null;
  const barMax = Math.max(...byType.map((t) => t.count));
  const width = (n: number) => `${(n / barMax) * 100}%`;

  const rows = useMemo(() => bundle!.projects
    .filter((p) => p.status === "ongoing" && (!sector || p.sector === sector))
    // Sorted by the model's slip probability. The old sort was rule risk, whose top twenty all
    // scored the same capped value, so the column read as twenty identical numbers.
    .sort((a, b) => (b.ml?.slip_prob ?? -1) - (a.ml?.slip_prob ?? -1) || b.risk.score - a.risk.score)
    .slice(0, TOP_N), [bundle, sector]);

  const csvRows = useMemo(() => rows.map((p) => ({
    project_code: p.project_code, project_name: p.project_name, state: p.state, sector: p.sector,
    physical_progress_pct: p.snapshots[p.snapshots.length - 1].physical_progress_pct,
    rule_risk_band: p.risk.band, rule_risk_score: p.risk.score, slip_prob_model: p.ml?.slip_prob ?? null,
  })), [rows]);

  // One decimal on the slip probability. At zero decimals the top twenty all read 96%, which is
  // a dead column; at two it would read 96.65 vs 96.64, precision this model cannot support.
  const columns: ColumnDef<Project, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "State", accessorKey: "state" },
    { header: "Progress", accessorFn: (p) => p.snapshots[p.snapshots.length - 1].physical_progress_pct, cell: (c) => <span className="num">{pct(c.getValue() as number | null)}</span> },
    { header: "Rule risk", accessorFn: (p) => p.risk.score, cell: (c) => <Badge text={c.row.original.risk.band} className={bandClass[c.row.original.risk.band]} /> },
    { header: "Slip prob. (model)", accessorFn: (p) => p.ml?.slip_prob ?? null, cell: (c) => <span className="num text-model">{share(c.getValue() as number | null, 1)}</span> },
  ];

  return (
    <div className="space-y-4">
      {/* The verdict, not a card. One thing the eye lands on first. */}
      <section className="rounded border border-line bg-surface px-5 py-4">
        <div className="text-xs uppercase tracking-wide text-muted">
          {snaps.length} reports parsed · {monthLabel(snaps[0])} to {monthLabel(latest)}
        </div>
        <p className="mt-1 max-w-4xl text-xl leading-snug">
          The Ministry&rsquo;s own published numbers contradict each other{" "}
          <span className="num font-semibold">{num(h.contradictions_arithmetic)}</span> times across these reports,
          and <span className="num font-semibold">{num(h.exits_total)}</span> projects left the panel without a
          public reason.
        </p>
        <div className="mt-2"><Caveat /></div>
      </section>

      {/* Four across, not eight. At eight the currency tiles are ~113px wide, which clips the
          "cr" off the value and ellipsises the exact figure on the sub line — and a clipped
          number is a wrong number. Four gives ~270px, enough for both in full. */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <KPI label={`Projects · ${latest}`} value={num(h.projects_latest)} />
        <KPI label="Revised cost" value={croreShort(h.cost_revised_total_cr)} sub={crore(h.cost_revised_total_cr)} />
        <KPI label="Recorded overrun" value={croreShort(h.overrun_total_cr)} sub={crore(h.overrun_total_cr)} hint="revised minus original" />
        <KPI label="Contradictions" value={num(h.contradictions_arithmetic)} hint="rule-based, across all reports parsed" />
        <KPI label="Left the panel" value={num(h.exits_total)} />
        <KPI label="Unreachable dates" value={num(h.unreachable_total)} hint="at own reported pace" />
        <KPI label="Statistical anomalies" value={num(h.statistical_anomalies)} hint="isolation forest, not arithmetic" model />
        <KPI label="Watchlist" value={num(h.watchlist_size)} model />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="mb-2 text-xs uppercase text-muted">Contradictions by type</div>
          <ul className="space-y-1.5">
            {arithmetic.map((t) => (
              <li key={t.type}>
                <div className="flex items-baseline justify-between gap-2 text-sm">
                  <span>{t.type}</span><span className="num text-muted">{num(t.count)}</span>
                </div>
                <div className="mt-0.5 h-1.5 rounded-xs bg-ground">
                  <div className="h-full rounded-xs bg-accent" style={{ width: width(t.count) }} />
                </div>
              </li>
            ))}
          </ul>
          {anomalies && (
            <>
              <hr className="my-3 border-line" />
              <div>
                <div className="flex items-baseline justify-between gap-2 text-sm">
                  <span className="text-model">{anomalies.type} · model</span>
                  <span className="num text-model">{num(anomalies.count)}</span>
                </div>
                <div className="mt-0.5 h-1.5 rounded-xs bg-ground">
                  <div className="h-full rounded-xs bg-model" style={{ width: width(anomalies.count) }} />
                </div>
                <p className="mt-1.5 text-xs text-muted">
                  Model output from an isolation forest, shown beside the rule-based ledger and never
                  counted into its total.
                </p>
              </div>
            </>
          )}
        </div>
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 text-xs uppercase text-muted">By sector</div>
          <table className="w-full"><tbody>{bundle!.findings.by_sector.slice().sort((a, b) => b.flagged - a.flagged).map((g) => <tr key={g.key} className="border-t border-line"><td>{g.key}</td><td className="num text-right">{num(g.flagged)} / {num(g.projects)} flagged</td><td className="num text-right text-critical">{num(g.red)} red</td></tr>)}</tbody></table>
          <p className="mt-2 text-xs text-muted">
            Sector here is a rollup of the agency string printed in the report. It is not a mapping to
            the official ministries, and one rollup may span several of them.
          </p>
        </div>
      </div>

      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase text-muted">Flagged projects by state</div>
        <IndiaMap />
      </div>

      <div className="flex items-baseline justify-between gap-3">
        <h2 className="text-lg font-semibold">Top {TOP_N} by model slip probability{sector ? ` · ${sector}` : ""}</h2>
        <CsvButton rows={csvRows} filename={`agrim-top-${TOP_N}-${latest}.csv`} />
      </div>
      <DataTable columns={columns} rows={rows} onRowClick={(p) => nav(`/project/${p.project_code}`)} height="720px" />
    </div>
  );
}
