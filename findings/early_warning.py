"""F3: can the project reach 100% by its own stated date at its own reported pace? No model, no training set."""
import numpy as np

from findings.panel import months, series, source

# JSON output rounds floats to 4 decimals (Global Constraints), so a slope below
# this magnitude rounds to 0.0000 and is not a real reported pace. np.polyfit on
# flat progress returns a floating-point denormal (~1e-16) instead of exact 0.0;
# without this guard that denormal slips past `v <= 0` and produces a ~1e17 ratio.
ZERO_VELOCITY_EPS = 5e-5


def velocity(rows):
    pts = [(months(rows[0]["snapshot"], r["snapshot"]), r["physical_progress_pct"]) for r in rows if r["physical_progress_pct"] is not None]
    if len(pts) < 2 or len({x for x, _ in pts}) < 2:
        return None
    x, y = zip(*pts)
    return float(np.polyfit(x, y, 1)[0])


def doc_current(row):
    return row["doc_revised"] or row["doc_original"]


def assess(rows):
    """rows: a project's rows ascending. Returns a dict for DOC_PASSED / DOC_UNREACHABLE, or None when not flagged."""
    last = rows[-1]
    prog = last["physical_progress_pct"]
    doc = doc_current(last)
    if prog is None or prog >= 100 or doc is None:
        return None
    rem = months(last["snapshot"], doc)
    v = velocity(rows)
    if rem <= 0:
        return {"type": "DOC_PASSED", "severity": "high", "velocity": v, "months_needed": None, "months_remaining": rem, "ratio": None,
                "detail": f"The stated completion date {doc} has passed and reported progress is {prog:g}%."}
    if v is None:
        return None
    if v < ZERO_VELOCITY_EPS:
        n = months(rows[0]["snapshot"], last["snapshot"])
        return {"type": "DOC_UNREACHABLE", "severity": "critical", "velocity": v, "months_needed": None, "months_remaining": rem, "ratio": None,
                "detail": f"No reported progress over {n} months; at this pace the stated date {doc} cannot be met."}
    need = (100 - prog) / v
    ratio = need / rem
    if ratio <= 1:
        return None
    sev = "critical" if ratio >= 2.0 else "high" if ratio >= 1.25 else "medium"
    return {"type": "DOC_UNREACHABLE", "severity": sev, "velocity": v, "months_needed": need, "months_remaining": rem, "ratio": ratio,
            "detail": f"At its own reported pace ({v:.2f} pt/month), this project needs {need:.0f} months; its own stated date {doc} leaves {rem}."}


def compute(panel):
    rows_out, flags = [], []
    for code, rs in series(panel).items():
        a = assess(rs)
        if a is None:
            continue
        srcs = [source(r) for r in rs]
        rows_out.append({"project_code": code, "project_name": rs[-1]["project_name"], "velocity_pct_per_month": a["velocity"],
                         "months_needed": a["months_needed"], "months_remaining": a["months_remaining"], "ratio": a["ratio"],
                         "severity": a["severity"], "sources": srcs})
        flags.append({"project_code": code, "type": a["type"], "severity": a["severity"], "from_snapshot": rs[0]["snapshot"],
                      "to_snapshot": rs[-1]["snapshot"], "before": doc_current(rs[-1]), "after": rs[-1]["physical_progress_pct"],
                      "detail": a["detail"], "sources": srcs})
    rows_out.sort(key=lambda r: (-(r["ratio"] if r["ratio"] is not None else 1e9), r["project_code"]))
    flags.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return {"rows": rows_out, "flags": flags}
