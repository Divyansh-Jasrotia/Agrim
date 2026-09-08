const inr2 = new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const inr0 = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
export const crore = (v: number | null | undefined) => (v == null ? "—" : `₹ ${inr2.format(v)} cr`);
export const num = (v: number | null | undefined, d = 0) => (v == null ? "—" : d === 0 ? inr0.format(v) : v.toFixed(d));
export const pct = (v: number | null | undefined, d = 1) => (v == null ? "—" : `${v.toFixed(d)}%`);
export const share = (v: number | null | undefined) => (v == null ? "—" : `${(v * 100).toFixed(0)}%`);
export const monthLabel = (ym: string | null | undefined) =>
  ym ? new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1, 1).toLocaleString("en-IN", { month: "short", year: "numeric" }) : "—";
export const sevClass: Record<string, string> = {
  critical: "bg-critical text-white", high: "bg-high text-white", medium: "bg-medium text-white", low: "bg-line text-ink", info: "bg-line text-muted",
};
export const bandClass: Record<string, string> = { red: "bg-critical text-white", amber: "bg-medium text-white", green: "bg-ok text-white" };
