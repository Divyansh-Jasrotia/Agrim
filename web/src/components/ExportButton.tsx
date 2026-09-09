import { useBundle } from "../data/store";
import { downloadCsv, toCsv } from "../lib/format";

export function ExportButton() {
  const { bundle } = useBundle();
  const onClick = () => {
    const rows = bundle!.findings.review_pack;
    const cols = ["project_code", "project_name", "state", "sector", "risk_band", "risk_score", "slip_prob", "expected_delay_months", "flag_types", "page"] as const;
    downloadCsv(toCsv(rows as unknown as Record<string, unknown>[], cols), `agrim-review-pack-${bundle!.findings.meta.snapshots.at(-1)}.csv`);
  };
  return <button onClick={onClick} className="rounded bg-accent px-3 py-1 text-sm text-white hover:opacity-90">Export review pack (CSV)</button>;
}
