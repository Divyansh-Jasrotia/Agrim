export function CsvButton({ rows, filename }: { rows: Record<string, unknown>[]; filename: string }) {
  function download() {
    if (!rows.length) return;
    const cols = Object.keys(rows[0]);
    const esc = (v: unknown) => {
      if (v == null) return "";                  // NULL stays empty. Never 0, never "NA".
      const s = String(v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  }
  return <button type="button" onClick={download} disabled={!rows.length}
    className="rounded border border-line px-2 py-1 text-xs hover:bg-ground disabled:opacity-50">Download this table (CSV)</button>;
}
