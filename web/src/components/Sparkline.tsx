import { useEChart } from "../lib/echart";

export function Sparkline({ labels, values, forecast, color, unit }:
  { labels: string[]; values: (number | null)[]; forecast?: number | null; color: string; unit: string }) {
  const xs = forecast != null ? [...labels, "next (model)"] : labels;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 28 },
    xAxis: { type: "category", data: xs, axisLabel: { fontSize: 10 } },
    yAxis: { type: "value", axisLabel: { fontSize: 10 }, name: unit, nameTextStyle: { fontSize: 10 } },
    tooltip: { trigger: "axis" },
    series: [
      { type: "line", data: values, color, showSymbol: true, symbolSize: 6, areaStyle: { opacity: 0.08 } },
      ...(forecast != null ? [{ type: "line" as const, data: [...values.map(() => null), forecast].map((v, i) => (i === values.length - 1 ? values[i] : v)),
        color: "#5B4B9A", lineStyle: { type: "dashed" as const }, showSymbol: true, symbolSize: 6 }] : []),
    ],
  }, [labels.join(), values.join(), forecast, color]);
  return <div ref={ref} style={{ height: "180px" }} />;
}
