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
    </div>
  );
}
