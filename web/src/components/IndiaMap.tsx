import * as echarts from "echarts";
import { useEffect, useRef } from "react";
import geo from "../assets/india_states.geo.json";
import { useBundle } from "../data/store";
import { num, pct } from "../lib/format";
import { mapCoverage, mapNames, norm } from "../lib/statemap";

let registered = false;

export function IndiaMap() {
  const { bundle } = useBundle();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current || !bundle) return;
    if (!registered) { echarts.registerMap("india", geo as never); registered = true; }
    const data = bundle.findings.by_state.map((s) => { const n = mapNames.get(norm(s.key)); return { name: n ?? s.key, value: s.flagged, projects: s.projects }; });
    const chart = echarts.init(ref.current);
    const max = Math.max(1, ...data.map((d) => d.value));
    chart.setOption({
      tooltip: { formatter: (p: { name: string; data?: { value: number; projects: number } }) => p.data ? `${p.name}<br/>${p.data.value} flagged of ${p.data.projects} projects` : `${p.name} — no matching data in this report` },
      visualMap: { min: 0, max, left: 0, bottom: 0, text: ["flagged", ""], inRange: { color: ["#EAF0F6", "#1F5FA8", "#B42318"] }, calculable: false },
      series: [{ type: "map", map: "india", roam: false, data, itemStyle: { borderColor: "#FFFFFF" }, emphasis: { label: { show: true, fontSize: 10 } } }],
    });
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => { window.removeEventListener("resize", onResize); chart.dispose(); };
  }, [bundle]);
  // A material share of the panel has no polygon to sit on. A viewer looking at the map has to be
  // able to see that from the map, not from a console warning they will never open.
  const cov = bundle ? mapCoverage(bundle.findings.by_state) : null;
  return (
    <>
      <div ref={ref} style={{ height: "420px" }} />
      {cov && cov.offMapProjects > 0 && (
        <p className="mt-1 text-xs text-muted">
          Not drawn on this map: {num(cov.offMapProjects)} of {num(cov.projects)} projects ({pct(100 * cov.offMapShare)}), including {num(cov.offMapFlagged)} that carry a flag.
          {" "}{num(cov.aggregateProjects)} of them are reported against several states at once, or as PAN India or Offshore, and have no single polygon;
          {" "}{num(cov.namedProjects)} sit under {num(cov.namedKeys.length)} territory names this map asset does not carry. Their numbers are in every table on the other screens.
        </p>
      )}
    </>
  );
}
