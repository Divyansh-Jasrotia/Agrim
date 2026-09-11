"""Reconstruct the delay classification the Flash Reports stopped printing.

The April 2014 report bucketed projects behind schedule into up to 12 months, 13-24,
25-60, and 61 months and above. The April 2026 report does not use the word at all.
The fields it still prints are enough to recompute the same bands. This is a
continuity-of-series reconstruction, not an accusation.
"""
from findings.panel import months, series, snapshots_present

BANDS = ["on_schedule", "d_1_12", "d_13_24", "d_25_60", "d_61_plus"]


def classify(doc_original, doc_revised, snapshot):
    """Months late against the original stated completion date. None if not classifiable."""
    if not doc_original:
        return None
    if doc_revised:
        return months(doc_original, doc_revised)
    # SPEC? An unrevised project past its own stated date is treated as late by the
    # elapsed months. The literal reading of "delayed against the stated schedule".
    gap = months(doc_original, snapshot)
    return gap if gap > 0 else 0


def _band(delay):
    if delay <= 0:
        return "on_schedule"
    if delay <= 12:
        return "d_1_12"
    if delay <= 24:
        return "d_13_24"
    if delay <= 60:
        return "d_25_60"
    return "d_61_plus"


def compute(panel):
    rows = []
    by_snapshot = {s: {b: 0 for b in BANDS} | {"doc_null": 0} for s in snapshots_present(panel)}
    for _, rs in series(panel).items():
        for r in rs:
            bucket = by_snapshot[r["snapshot"]]
            delay = classify(r["doc_original"], r["doc_revised"], r["snapshot"])
            if delay is None:
                bucket["doc_null"] += 1
            else:
                bucket[_band(delay)] += 1
    for s in snapshots_present(panel):
        b = by_snapshot[s]
        rows.append({"snapshot": s, **{k: b[k] for k in BANDS},
                     "classifiable": sum(b[k] for k in BANDS), "doc_null": b["doc_null"]})
    return {"bands": BANDS, "rows": rows}
