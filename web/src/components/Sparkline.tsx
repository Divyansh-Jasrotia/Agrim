import { useEChart } from "../lib/echart";

const INK = "#0E1A2B";
const CRITICAL = "#B42318";
const MODEL = "#5B4B9A";

// A trend line is not a severity, so it is drawn in ink. Only the points a rule actually flagged
// are drawn in the critical colour. Drawing a collapsing expenditure line in the ok green, as
// this did, told the reader the opposite of the finding.
export function Sparkline({ labels, values, forecast, unit, alertLabels = [] }:
  { labels: string[]; values: (number | null)[]; forecast?: number | null; unit: string; alertLabels?: string[] }) {
  const xs = forecast != null ? [...labels, "next (model)"] : labels;
  const flagged = labels.map((l, i) => (alertLabels.includes(l) ? [i, values[i]] : null)).filter(Boolean) as [number, number][];
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 28 },
    xAxis: { type: "category", data: xs, axisLabel: { fontSize: 10 } },
    yAxis: { type: "value", axisLabel: { fontSize: 10 }, name: unit, nameTextStyle: { fontSize: 10 } },
    tooltip: { trigger: "axis" },
    series: [
      { type: "line", data: values, color: INK, showSymbol: true, symbolSize: 6, areaStyle: { opacity: 0.06 } },
      ...(flagged.length ? [{ type: "scatter" as const, data: flagged, color: CRITICAL, symbolSize: 10,
        tooltip: { formatter: "flagged by a rule" }, z: 5 }] : []),
      ...(forecast != null ? [{ type: "line" as const, data: [...values.map(() => null), forecast].map((v, i) => (i === values.length - 1 ? values[i] : v)),
        color: MODEL, lineStyle: { type: "dashed" as const }, showSymbol: true, symbolSize: 6 }] : []),
    ],
  }, [labels.join(), values.join(), forecast, alertLabels.join()]);
  return <div ref={ref} style={{ height: "180px" }} />;
}
