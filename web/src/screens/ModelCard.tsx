import { useBundle } from "../data/store";

export function ModelCard() {
  const { bundle } = useBundle();
  const mc = bundle!.modelCard;
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
      <p className="text-xs text-muted">Map boundary limitation: the committed map asset predates the 2019 reorganisation of Jammu &amp; Kashmir, so Jammu &amp; Kashmir is drawn as a single undivided polygon and Ladakh has no polygon of its own — Ladakh cannot appear on the map at all. The map's state names also do not match the project data for four other states or union territories (a misspelled Arunachal Pradesh, Andaman &amp; Nicobar, Delhi, and the pre-merger split of Dadra &amp; Nagar Haveli and Daman &amp; Diu). Ladakh and these four will show as having no matching data on the map even though their numbers are present in the underlying report data.</p>
    </div>
  );
}
