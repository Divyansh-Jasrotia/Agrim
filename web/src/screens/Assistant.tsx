import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useBundle } from "../data/store";

const OLLAMA = "http://localhost:11434";

export function Assistant() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const [sel, setSel] = useState(0);
  const [code, setCode] = useState("");
  const [live, setLive] = useState(false);
  const [q, setQ] = useState("");
  const [a, setA] = useState<string | null>(null);
  useEffect(() => { fetch(`${OLLAMA}/`).then((r) => r.text()).then((t) => setLive(t.includes("Ollama is running"))).catch(() => setLive(false)); }, []);
  const qa = bundle!.findings.assistant;
  const ask = async () => {
    const p = bundle!.byCode.get(code.trim());
    const facts = p ? JSON.stringify({ project: p.project_name, code: p.project_code, snapshots: p.snapshots, flags: p.flags.map((f) => f.detail), risk: p.risk, ml: p.ml }) : "No project selected; answer only from general knowledge of the ledger structure.";
    setA("…");
    try {
      const r = await fetch(`${OLLAMA}/api/generate`, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: bundle!.briefs?.[0]?.model ?? "qwen2.5:3b", stream: false, options: { seed: 0, temperature: 0 },
          prompt: `You answer a monitoring officer using ONLY these facts. Do not invent numbers.\nFACTS: ${facts}\nQUESTION: ${q}\nANSWER:` }) });
      const j = await r.json();
      setA(j.response ?? "(no answer)");
    } catch (e) { setA(`Local model unavailable: ${(e as Error).message}`); }
  };
  return (
    <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
      <div className="space-y-2">
        <div className="rounded border border-line bg-surface p-3">
          <label className="text-xs uppercase text-muted">Open a project by code</label>
          <div className="mt-1 flex gap-2"><input value={code} onChange={(e) => setCode(e.target.value)} className="num w-full rounded border border-line px-2 py-1" placeholder="e.g. a code from the Ledger" />
            <button className="rounded bg-accent px-3 text-sm text-white" onClick={() => bundle!.byCode.has(code.trim()) && nav(`/project/${code.trim()}`)}>Open</button></div>
          {code && !bundle!.byCode.has(code.trim()) && <div className="mt-1 text-xs text-critical">No project with that code in the parsed reports.</div>}
        </div>
        <div className="rounded border border-line bg-surface">
          {qa.map((x, i) => <button key={x.id} onClick={() => setSel(i)} className={`block w-full border-b border-line px-3 py-2 text-left text-sm last:border-b-0 ${sel === i ? "bg-ground font-medium" : ""}`}>{x.question}</button>)}
        </div>
      </div>
      <div className="space-y-4">
        <div className="rounded border border-line bg-surface p-4">
          <div className="text-xs uppercase text-muted">Answer · from the ledger, deterministic</div>
          <p className="mt-2 text-sm">{qa[sel]?.answer}</p>
          {qa[sel]?.sources.length > 0 && <div className="mt-2 flex flex-wrap gap-1">{qa[sel].sources.map((s, i) => <span key={i} className="num rounded border border-line px-1 text-xs text-muted">{s.snapshot} p.{s.page}</span>)}</div>}
        </div>
        {live ? (
          <div className="rounded border border-model bg-surface p-4">
            <div className="text-xs uppercase text-model">Ask the local model (Ollama detected) · grounded on the project you typed above</div>
            <textarea value={q} onChange={(e) => setQ(e.target.value)} className="mt-2 w-full rounded border border-line p-2 text-sm" rows={3} placeholder="Why does this project look risky?" />
            <button onClick={ask} className="mt-2 rounded bg-model px-3 py-1 text-sm text-white">Ask</button>
            {a && <p className="mt-2 text-sm">{a}</p>}
          </div>
        ) : <div className="text-xs text-muted">Live model mode is off (no local Ollama detected). Every answer above is computed from the ledger and cannot hallucinate.</div>}
      </div>
    </div>
  );
}
