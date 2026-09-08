import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, share } from "../lib/format";

export function Fields() {
  const { bundle } = useBundle();
  const fa = bundle!.findings.field_audit;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 24, bottom: 28 }, tooltip: {}, legend: { top: 0 },
    xAxis: { type: "category", data: fa.terminal_digit.map((d) => String(d.digit)), name: "last digit of reported progress" },
    yAxis: { type: "value", name: "share" },
    series: [
      { name: "reported", type: "bar", data: fa.terminal_digit.map((d) => d.share), color: "#1F5FA8" },
      { name: "if measured (uniform)", type: "line", data: fa.terminal_digit.map(() => 0.1), color: "#4B5A6B", lineStyle: { type: "dashed" }, showSymbol: false },
    ],
  }, [fa]);
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Field Audit · what the form actually captures</h1>
      <p className="max-w-3xl text-sm text-muted">A genuinely measured percentage spreads its last digit evenly. Round-number clustering means the field is estimated, not measured. This is the supply-side answer to dimension (c): which fields carry information as filled.</p>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Whole numbers</div><div className="num text-2xl">{share(fa.whole_number_share)}</div><div className="text-xs text-muted">expected ≈ 1% if measured</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 5</div><div className="num text-2xl">{share(fa.multiple_of_5_share)}</div><div className="text-xs text-muted">expected ≈ 20% of whole numbers</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 10</div><div className="num text-2xl">{share(fa.multiple_of_10_share)}</div><div className="text-xs text-muted">expected ≈ 10% of whole numbers</div></div>
      </div>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "260px" }} /></div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">Expenditure never updated across the reports, by agency (agencies with ≥5 projects)</div>
        {fa.staleness_by_agency.length === 0 && <div className="text-sm text-muted">No agency has five or more projects in this panel.</div>}
        <table className="w-full text-sm"><tbody>{fa.staleness_by_agency.slice(0, 15).map((a) => <tr key={a.agency_raw} className="border-t border-line"><td>{a.agency_raw}</td><td className="num text-right">{num(a.projects)} projects</td><td className="num text-right">{share(a.share_unchanged)} unchanged</td></tr>)}</tbody></table>
      </div>
    </div>
  );
}
