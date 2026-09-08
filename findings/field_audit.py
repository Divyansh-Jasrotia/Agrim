"""F5: which reported fields look measured and which look guessed. Terminal-digit clustering + per-agency staleness."""
import math
from collections import Counter, defaultdict

from findings.panel import latest, series

BANDS = [(105, "very accurate"), (110, "relatively accurate"), (125, "approximate"), (175, "rough")]


def whipple_index(digit_counts):
    """Digit-heaping index over terminal digits. 100 = no preference, 500 = every value on 0 or 5.

    Whipple, not Benford: physical progress is bounded 0-100, so Benford's Law does not apply.
    """
    n = sum(digit_counts.values())
    if not n:
        return None
    return round(100.0 * (digit_counts.get(0, 0) + digit_counts.get(5, 0)) / (0.2 * n), 4)


def whipple_band(w):
    if w is None:
        return None
    for limit, name in BANDS:
        if w < limit:
            return name
    return "very rough"


def compute(panel):
    last = latest(panel)
    ser = series(panel)
    vals = [r["physical_progress_pct"] for rs in ser.values() for r in rs if r["snapshot"] == last and r["physical_progress_pct"] is not None]
    n = len(vals)
    digits = Counter(int(math.floor(v)) % 10 for v in vals)
    whole = [v for v in vals if float(v).is_integer()]
    by_agency = defaultdict(list)
    for code, rs in ser.items():
        if len(rs) < 2:
            continue
        agency = next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None)
        if agency is None:
            continue
        exps = [r["expenditure_cum_cr"] for r in rs]
        unchanged = all(a is not None and b is not None and a == b for a, b in zip(exps, exps[1:]))
        by_agency[agency].append(unchanged)
    stale = [{"agency_raw": a, "projects": len(v), "share_unchanged": round(sum(v) / len(v), 4)}
             for a, v in sorted(by_agency.items()) if len(v) >= 5]
    stale.sort(key=lambda d: (-d["share_unchanged"], d["agency_raw"]))
    return {"snapshot": last,
            "terminal_digit": [{"digit": d, "count": digits.get(d, 0), "share": round(digits.get(d, 0) / n, 4) if n else 0.0} for d in range(10)],
            "whole_number_share": round(len(whole) / n, 4) if n else 0.0,
            "multiple_of_5_share": round(sum(1 for v in whole if int(v) % 5 == 0) / n, 4) if n else 0.0,
            "multiple_of_10_share": round(sum(1 for v in whole if int(v) % 10 == 0) / n, 4) if n else 0.0,
            "whipple_index": whipple_index(digits),
            "whipple_band": whipple_band(whipple_index(digits)),
            "staleness_by_agency": stale}
