import * as echarts from "echarts";
import { useEffect, useRef } from "react";
import geo from "../assets/india_states.geo.json";
import { useBundle } from "../data/store";

const NAME_PROP = "ST_NM";
const norm = (s: string) => s.toLowerCase().replace(/&/g, "and").replace(/[^a-z]/g, "");
let registered = false;

export function IndiaMap() {
  const { bundle } = useBundle();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current || !bundle) return;
    const g = geo as unknown as { features: { properties: Record<string, string> }[] };
    if (!registered) { echarts.registerMap("india", geo as never); registered = true; }
    const names = new Map(g.features.map((f) => [norm(f.properties[NAME_PROP]), f.properties[NAME_PROP]]));
    const unmatched: string[] = [];
    const data = bundle.findings.by_state.map((s) => { const n = names.get(norm(s.key)); if (!n) unmatched.push(s.key); return { name: n ?? s.key, value: s.flagged, projects: s.projects }; });
    if (unmatched.length) console.warn("states not matched to map:", unmatched);
    const chart = echarts.init(ref.current);
    const max = Math.max(1, ...data.map((d) => d.value));
    chart.setOption({
      tooltip: { formatter: (p: { name: string; data?: { value: number; projects: number } }) => `${p.name}<br/>${p.data?.value ?? 0} flagged of ${p.data?.projects ?? 0} projects` },
      visualMap: { min: 0, max, left: 0, bottom: 0, text: ["flagged", ""], inRange: { color: ["#EAF0F6", "#1F5FA8", "#B42318"] }, calculable: false },
      series: [{ type: "map", map: "india", roam: false, data, itemStyle: { borderColor: "#FFFFFF" }, emphasis: { label: { show: true, fontSize: 10 } } }],
    });
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => { window.removeEventListener("resize", onResize); chart.dispose(); };
  }, [bundle]);
  return <div ref={ref} style={{ height: "420px" }} />;
}
