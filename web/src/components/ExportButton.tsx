import { useBundle } from "../data/store";

export function ExportButton() {
  const { bundle } = useBundle();
  const onClick = () => {
    const rows = bundle!.findings.review_pack;
    const cols = ["project_code", "project_name", "state", "sector", "risk_band", "risk_score", "slip_prob", "expected_delay_months", "flag_types", "page"] as const;
    const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = `agrim-review-pack-${bundle!.findings.meta.snapshots.at(-1)}.csv`; a.click();
    URL.revokeObjectURL(url);
  };
  return <button onClick={onClick} className="rounded bg-accent px-3 py-1 text-sm text-white hover:opacity-90">Export review pack (CSV)</button>;
}
