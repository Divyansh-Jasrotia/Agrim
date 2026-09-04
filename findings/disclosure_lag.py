"""F6: for each revised-DoC filing, the earliest earlier report at which F3 already said the then-stated date was unreachable."""
import statistics

from findings.early_warning import assess
from findings.panel import months, series


def compute(panel):
    rows, any_backcastable = [], False
    for code, rs in series(panel).items():
        for k in range(1, len(rs)):
            if rs[k]["doc_revised"] == rs[k - 1]["doc_revised"]:
                continue
            filed_at = rs[k]["snapshot"]
            first = None
            for j in range(1, k):                      # prefixes rs[:j+1] with >= 2 snapshots, strictly before the filing
                any_backcastable = True
                a = assess(rs[:j + 1])
                if a is not None and a["type"] == "DOC_UNREACHABLE":
                    first = rs[j]["snapshot"]
                    break
            rows.append({"project_code": code, "filed_at": filed_at, "first_unreachable": first,
                         "lag_months": months(first, filed_at) if first else None})
    lags = [r["lag_months"] for r in rows if r["lag_months"] is not None]
    return {"status": "computed" if any_backcastable else "not_computed",
            "median_lag_months": float(statistics.median(lags)) if lags else None, "rows": rows}
