import geo from "../assets/india_states.geo.json";
import type { Group } from "../types/findings";

const NAME_PROP = "ST_NM";

/** The map's own name matching. The disclosure must count exactly what the map draws, so
 *  both the map and the model card import this one function rather than each having a copy. */
export const norm = (s: string) => s.toLowerCase().replace(/&/g, "and").replace(/[^a-z]/g, "");

const features = (geo as unknown as { features: { properties: Record<string, string> }[] }).features;
export const mapNames = new Map(features.map((f) => [norm(f.properties[NAME_PROP]), f.properties[NAME_PROP]]));

/** A key naming several territories at once (or none) has no single polygon by construction.
 *  This is a different reason for being off the map than a name the asset spells differently,
 *  and the disclosure has to separate the two or it misstates the cause. */
const isAggregate = (key: string) => /^multi-state/i.test(key) || /^pan india$/i.test(key) || /^offshore$/i.test(key);

export type MapCoverage = {
  projects: number;
  flagged: number;
  offMapProjects: number;
  offMapFlagged: number;
  offMapShare: number;
  offMapKeys: number;
  totalKeys: number;
  aggregateKeys: number;
  aggregateProjects: number;
  namedKeys: string[];
  namedProjects: number;
};

/** How much of the panel the state map cannot show, and why. Everything is derived from the
 *  committed geojson and the findings bundle at runtime; nothing here is a typed-in count. */
export function mapCoverage(byState: Group[]): MapCoverage {
  const sum = (rows: Group[], f: (g: Group) => number) => rows.reduce((a, g) => a + f(g), 0);
  const off = byState.filter((g) => !mapNames.has(norm(g.key)));
  const agg = off.filter((g) => isAggregate(g.key));
  const named = off.filter((g) => !isAggregate(g.key));
  const projects = sum(byState, (g) => g.projects);
  const offMapProjects = sum(off, (g) => g.projects);
  return {
    projects,
    flagged: sum(byState, (g) => g.flagged),
    offMapProjects,
    offMapFlagged: sum(off, (g) => g.flagged),
    offMapShare: projects ? offMapProjects / projects : 0,
    offMapKeys: off.length,
    totalKeys: byState.length,
    aggregateKeys: agg.length,
    aggregateProjects: sum(agg, (g) => g.projects),
    namedKeys: named.map((g) => g.key).sort(),
    namedProjects: sum(named, (g) => g.projects),
  };
}
