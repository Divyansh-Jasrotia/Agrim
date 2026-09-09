import { downloadCsv, toCsv } from "../lib/format";

export function CsvButton({ rows, filename }: { rows: Record<string, unknown>[]; filename: string }) {
  const download = () => { if (rows.length) downloadCsv(toCsv(rows, Object.keys(rows[0])), filename); };
  return <button type="button" onClick={download} disabled={!rows.length}
    className="rounded border border-line px-2 py-1 text-xs hover:bg-ground disabled:opacity-50">Download this table (CSV)</button>;
}
