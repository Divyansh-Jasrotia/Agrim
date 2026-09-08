"""M4: month-to-month changes that are unusual even when arithmetically possible. Never re-labels F1's impossibilities."""
import math

import numpy as np
from sklearn.ensemble import IsolationForest

from findings.panel import months, pairs_present, series, source

SEED = 0
SHARE = 0.02


def _feat(a, b):
    def d(k):
        return (b[k] - a[k]) if a[k] is not None and b[k] is not None else 0.0
    cr = a["cost_revised_cr"] or 0.0
    return [d("expenditure_cum_cr"), d("expenditure_cum_cr") / cr if cr else 0.0, d("physical_progress_pct"), d("cost_revised_cr"),
            float(months(a["snapshot"], b["snapshot"])), a["physical_progress_pct"] if a["physical_progress_pct"] is not None else 50.0]


def run(panel):
    ser = series(panel)
    rows, meta = [], []
    for pid, t0, t1 in pairs_present(panel):
        for code, rs in ser.items():
            d = {r["snapshot"]: r for r in rs}
            if t0 in d and t1 in d:
                rows.append(_feat(d[t0], d[t1]))
                meta.append((pid, code, d[t0], d[t1]))
    X = np.asarray(rows, dtype=float)
    scores = -IsolationForest(contamination="auto", random_state=SEED).fit(X).score_samples(X)
    flagged, extra, per = [], [], {}
    for pid in sorted({m[0] for m in meta}):
        idx = [i for i, m in enumerate(meta) if m[0] == pid]
        k = max(1, math.ceil(SHARE * len(idx)))
        top = sorted(idx, key=lambda i: (-scores[i], meta[i][1]))[:k]
        for i in top:
            _, code, a, b = meta[i]
            src = [source(a), source(b)]
            flagged.append({"project_code": code, "pair": pid, "score": float(scores[i]), "sources": src})
            extra.append({"project_code": code, "type": "STAT_ANOMALY", "severity": "info", "from_snapshot": a["snapshot"], "to_snapshot": b["snapshot"],
                          "before": a["expenditure_cum_cr"], "after": b["expenditure_cum_cr"],
                          "detail": f"Month-to-month change between {a['snapshot']} and {b['snapshot']} is in the top {int(SHARE * 100)}% most unusual for that pair (isolation score {scores[i]:.3f}).",
                          "sources": src})
    flagged_codes = {f["project_code"] for f in flagged}
    for i, (pid, code, a, b) in enumerate(meta):
        p = per.setdefault(code, {"anomaly_score": 0.0, "anomaly_flag": code in flagged_codes})
        p["anomaly_score"] = max(p["anomaly_score"], float(scores[i]))
    flagged.sort(key=lambda f: (f["pair"], -f["score"], f["project_code"]))
    extra.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return {"n": int(len(rows)), "contamination": "auto", "flagged": flagged}, per, extra
