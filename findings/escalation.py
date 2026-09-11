"""Per-rollup delay rate, direction of travel, and an escalation flag.

Implements the structured escalation matrix a parliamentary committee recommended:
flag rollups whose delay rate exceeds 50% and is not improving. No report number or
date is cited here; the attribution is unresolved and the finding stands on the counts.

The rollup key is the agency-derived sector of D15. It is a rollup, not a mapping to
the 17 official ministries, and any screen showing it must say so.
"""
from findings.delay_series import classify
from findings.panel import series, snapshots_present

THRESHOLD_PCT = 50.0
# A percentage over a handful of projects is not a rate. Official statistics convention is to
# suppress or flag a rate on a small denominator, so a rollup below this many classifiable
# projects is still shown with its real numbers but is never flagged for escalation.
MIN_CLASSIFIABLE = 10


def _rate(delayed, classifiable):
    return round(100.0 * delayed / classifiable, 4) if classifiable else None


def compute(panel, sectors):
    snaps = snapshots_present(panel)
    # SPEC? "its rate in the first snapshot where it had classifiable projects" reads two ways.
    # Literal reading taken: first is the panel's first snapshot, full stop. A rollup with no
    # classifiable projects there gets first_rate_pct None and improving None, rather than
    # scanning forward to the earliest snapshot that did have data.
    first, last = snaps[0], snaps[-1]
    agg = {}
    for code, rs in series(panel).items():
        key = sectors.get(code) or "UNKNOWN"
        a = agg.setdefault(key, {"projects": set(), "first": [0, 0], "last": [0, 0]})
        a["projects"].add(code)
        for r in rs:
            if r["snapshot"] not in (first, last):
                continue
            slot = a["first"] if r["snapshot"] == first else a["last"]
            delay = classify(r["doc_original"], r["doc_revised"], r["snapshot"])
            if delay is None:
                continue
            slot[1] += 1
            if delay > 0:
                slot[0] += 1
    rows = []
    for key, a in agg.items():
        d_last, c_last = a["last"]
        d_first, c_first = a["first"]
        rate, first_rate = _rate(d_last, c_last), _rate(d_first, c_first)
        improving = None if first_rate is None or rate is None else rate < first_rate
        rows.append({"key": key, "projects": len(a["projects"]), "classifiable": c_last, "delayed": d_last,
                     "delay_rate_pct": rate, "first_rate_pct": first_rate, "improving": improving,
                     "escalate": bool(rate is not None and rate > THRESHOLD_PCT and improving is not True
                                      and c_last >= MIN_CLASSIFIABLE)})
    rows.sort(key=lambda r: (-(r["delay_rate_pct"] if r["delay_rate_pct"] is not None else -1), r["key"]))
    return {"threshold_pct": THRESHOLD_PCT, "min_classifiable": MIN_CLASSIFIABLE, "rows": rows}
