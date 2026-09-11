import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, share } from "../lib/format";

export function Fields() {
  const { bundle } = useBundle();
  const fa = bundle!.findings.field_audit;
  // multiple_of_5_share / multiple_of_10_share are shares of ALL reported values, but "about 20%"
  // and "about 10%" are expectations among WHOLE numbers. Comparing 17% of all values with 20% of
  // whole numbers made the clustering look absent on the screen whose whole point is that it is
  // there. Restate the observed figures on the whole-number denominator the expectation uses.
  const w = fa.whole_number_share;
  const m5 = w ? fa.multiple_of_5_share / w : null;
  const m10 = w ? fa.multiple_of_10_share / w : null;
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
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Whole numbers</div><div className="num text-2xl">{share(w)}</div><div className="text-xs text-muted">of all reported values · expected ≈ 1% of all values if measured</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 5</div><div className="num text-2xl">{share(m5)}</div><div className="text-xs text-muted">of whole-number values · expected ≈ 20% of whole-number values</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 10</div><div className="num text-2xl">{share(m10)}</div><div className="text-xs text-muted">of whole-number values · expected ≈ 10% of whole-number values</div></div>
      </div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="text-xs uppercase tracking-wide text-muted">Whipple&rsquo;s index</div>
        <div className="num text-2xl">{fa.whipple_index == null ? "—" : fa.whipple_index.toFixed(1)}
          {fa.whipple_band && <span className="ml-2 text-base text-muted">{fa.whipple_band}</span>}</div>
        <p className="mt-1 max-w-3xl text-xs text-muted">
          The conventional measure of digit heaping. It compares how often a value ends in 0 or 5 with how
          often it would if the last digit were evenly spread. An index of one hundred means no
          preference; five hundred means every value sits on a 0 or a 5. The bands shown are the
          standard ones. Benford&rsquo;s Law does not apply here: it describes the leading digits of
          quantities spanning orders of magnitude, and physical progress is a bounded percentage.
        </p>
      </div>
      <p className="max-w-3xl text-xs text-muted">Each card compares like with like: the first is a share of every reported progress value, the second and third are shares of the whole-number values only, which is the denominator the ≈20% and ≈10% expectations are stated on. Reading a share of all values against an expectation stated per whole number understates the clustering.</p>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "260px" }} /></div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">Expenditure never updated across the reports, by agency (agencies with ≥5 projects)</div>
        {fa.staleness_by_agency.length === 0 && <div className="text-sm text-muted">No agency has five or more projects in this panel.</div>}
        <table className="w-full text-sm"><tbody>{fa.staleness_by_agency.slice(0, 15).map((a) => <tr key={a.agency_raw} className="border-t border-line"><td>{a.agency_raw}</td><td className="num text-right">{num(a.projects)} projects</td><td className="num text-right">{share(a.share_unchanged)} unchanged</td></tr>)}</tbody></table>
      </div>
    </div>
  );
}
