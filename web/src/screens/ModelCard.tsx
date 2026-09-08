import { useBundle } from "../data/store";
import { num, pct } from "../lib/format";
import { mapCoverage } from "../lib/statemap";

export function ModelCard() {
  const { bundle } = useBundle();
  const mc = bundle!.modelCard;
  // Measured against the committed geojson with the map's own name matching, not asserted.
  const cov = mapCoverage(bundle!.findings.by_state);
  if (!mc) return <div className="rounded border border-line bg-surface p-6 text-muted">model_card.json is not present.</div>;
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-xl font-semibold">Model Card · generated {mc.generated_at}</h1>
      {mc.sections.map((s) => (
        <section key={s.title} className="rounded border border-line bg-surface p-4">
          <h2 className="mb-2 font-semibold">{s.title}</h2>
          <ul className="list-disc space-y-1 pl-5 text-sm">{s.lines.map((l, i) => <li key={i}>{l}</li>)}</ul>
        </section>
      ))}
      <p className="text-xs text-muted">Source data: MoSPI Flash Reports (public). Map: DataMeet India maps (CC BY 4.0). Stack: Python, pdfplumber, scikit-learn, SHAP, Ollama, React, ECharts. All open source.</p>
      <section className="rounded border border-line bg-surface p-4 text-xs text-muted">
        <h2 className="mb-2 text-sm font-semibold text-ink">What the state map does not show</h2>
        <p>
          The map matches {num(cov.totalKeys - cov.offMapKeys)} of the {num(cov.totalKeys)} state values in the report to a polygon.
          The other {num(cov.offMapKeys)} are not drawn at all: {num(cov.offMapProjects)} projects, {pct(100 * cov.offMapShare)} of the {num(cov.projects)} in the panel,
          of which {num(cov.offMapFlagged)} carry a flag and so never appear on the map even though they are flagged.
        </p>
        <p className="mt-2">
          Most of this is not a boundary-vintage problem. {num(cov.aggregateProjects)} of those projects sit under {num(cov.aggregateKeys)} keys that name several states at once,
          or name no state at all (PAN India, Offshore). No single polygon can represent them; choropleth is the wrong shape for that data, not a bug in the asset.
        </p>
        <p className="mt-2">
          The remaining {num(cov.namedProjects)} sit under {num(cov.namedKeys.length)} single-territory names the committed asset does not carry: {cov.namedKeys.join("; ")}.
          The asset predates the 2019 reorganisation, so Ladakh has no polygon of its own and Dadra &amp; Nagar Haveli and Daman &amp; Diu are still drawn as two separate
          pre-merger units; the rest are spelling and long-form differences between the asset and the report ("Arunanchal Pradesh", "NCT of Delhi", "Andaman &amp; Nicobar Island").
          Every one of these projects is present in the ledger, the tables and the review pack; only the map omits them.
        </p>
      </section>
    </div>
  );
}
