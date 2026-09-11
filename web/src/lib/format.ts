const inr2 = new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const inr0 = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
export const crore = (v: number | null | undefined) => (v == null ? "—" : `₹ ${inr2.format(v)} cr`);
// A twelve-digit crore figure does not fit a tile. Show it abbreviated, exact value beneath.
// LAKH is written as a product so the literal guard in tools/validate.py stays meaningful.
const LAKH = 1000 * 100;
const THOUSAND = 1000;
export const croreShort = (v: number | null | undefined) => {
  if (v == null) return "—";
  if (v >= LAKH) return `₹ ${(v / LAKH).toFixed(2)} L cr`;
  if (v >= THOUSAND) return `₹ ${(v / THOUSAND).toFixed(2)} K cr`;
  return crore(v);
};
export const num = (v: number | null | undefined, d = 0) => (v == null ? "—" : d === 0 ? inr0.format(v) : v.toFixed(d));
export const pct = (v: number | null | undefined, d = 1) => (v == null ? "—" : `${v.toFixed(d)}%`);
export const share = (v: number | null | undefined, d = 0) => (v == null ? "—" : `${(v * 100).toFixed(d)}%`);
export const monthLabel = (ym: string | null | undefined) =>
  ym ? new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1, 1).toLocaleString("en-IN", { month: "short", year: "numeric" }) : "—";
export const sevClass: Record<string, string> = {
  critical: "bg-critical text-white", high: "bg-high text-white", medium: "bg-medium text-white", low: "bg-line text-ink", info: "bg-line text-muted",
};
export const bandClass: Record<string, string> = { red: "bg-critical text-white", amber: "bg-medium text-white", green: "bg-ok text-white" };

// One CSV writer for every export, so the formula guard cannot be dropped by a new caller.
// Excel and Sheets evaluate a cell starting with = + - or @ as a formula even inside quotes, so a
// project name beginning with one of those would execute on open. A leading apostrophe forces the
// cell to text and is stripped by the spreadsheet on display.
const FORMULA = /^[=+\-@\t\r]/;
export const csvCell = (v: unknown) => {
  if (v == null) return "";                       // NULL stays an empty field. Never 0, never "NA".
  const t = String(v);
  return `"${(FORMULA.test(t) ? `'${t}` : t).replace(/"/g, '""')}"`;
};
export const toCsv = (rows: Record<string, unknown>[], cols: readonly string[]) =>
  [cols.join(","), ...rows.map((r) => cols.map((c) => csvCell(r[c])).join(","))].join("\n");
export const downloadCsv = (csv: string, filename: string) => {
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  // a.click() only queues the download. Revoking synchronously aborts it in Firefox, so defer the
  // revoke past the current task and let the browser read the blob first.
  setTimeout(() => URL.revokeObjectURL(url), 0);
};
