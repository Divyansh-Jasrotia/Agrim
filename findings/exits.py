"""F2: projects that leave the monitored panel between consecutive reports, with their last observed state."""
from findings.panel import pairs_present, series, snapshots_present, source


def _partition(prog):
    if prog is None:
        return "UNKNOWN"
    if prog >= 95:
        return "LAST_SEEN_GE_95"
    if prog >= 50:
        return "LAST_SEEN_50_95"
    return "LAST_SEEN_LT_50"


def compute(panel, aggregates=None):
    ser = series(panel)
    snaps = snapshots_present(panel)
    present = {s: {} for s in snaps}
    for code, rs in ser.items():
        for r in rs:
            present[r["snapshot"]][code] = r
    pairs, rows, seen = [], [], set()
    for pid, a, b in pairs_present(panel):
        exited = sorted(set(present[a]) - set(present[b]))
        entered = sorted(set(present[b]) - set(present[a]))
        agg_b = (aggregates or {}).get(b) or {}
        pairs.append({"from": a, "to": b, "exited": len(exited), "entered": len(entered),
                      "exited_cost_revised_cr": round(sum(present[a][c]["cost_revised_cr"] or 0.0 for c in exited), 2),
                      "commissioned_printed": agg_b.get("commissioned")})
        for code in exited:
            last = present[a][code]
            if (code, a) in seen:
                continue
            seen.add((code, a))
            rows.append({"project_code": code, "project_name": last["project_name"], "last_seen": a,
                         "last_progress_pct": last["physical_progress_pct"], "last_expenditure_cr": last["expenditure_cum_cr"],
                         "last_cost_revised_cr": last["cost_revised_cr"], "partition": _partition(last["physical_progress_pct"]),
                         "sources": [source(last)]})
    status = {}
    for code, rs in ser.items():
        first, last = rs[0]["snapshot"], rs[-1]["snapshot"]
        status[code] = ("ongoing" if last == snaps[-1] else "exited", first, last)
    return {"pairs": pairs, "rows": rows, "status": status}
