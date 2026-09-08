import { useBundle } from "../data/store";

export function ExportButton() {
  const { bundle } = useBundle();
  const onClick = () => {
    const rows = bundle!.findings.review_pack;
    const cols = ["project_code", "project_name", "state", "sector", "risk_band", "risk_score", "slip_prob", "expected_delay_months", "flag_types", "page"] as const;
    // Excel and Sheets evaluate a cell starting with = + - or @ as a formula even inside quotes, so a
    // project name beginning with one of those would execute on open. A leading apostrophe forces the
    // cell to text; it is the standard mitigation and is stripped by the spreadsheet on display.
    const esc = (v: unknown) => {
      const t = String(v ?? "");
      return `"${(/^[=+\-@\t\r]/.test(t) ? `'${t}` : t).replace(/"/g, '""')}"`;
    };
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = `agrim-review-pack-${bundle!.findings.meta.snapshots.at(-1)}.csv`; a.click();
    // a.click() only queues the download. Revoking synchronously aborts it in Firefox, so defer the
    // revoke past the current task and let the browser read the blob first.
    setTimeout(() => URL.revokeObjectURL(url), 0);
  };
  return <button onClick={onClick} className="rounded bg-accent px-3 py-1 text-sm text-white hover:opacity-90">Export review pack (CSV)</button>;
}
