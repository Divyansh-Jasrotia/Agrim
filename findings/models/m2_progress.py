"""M2: next-month physical progress (points/month) vs no-change and the project's own velocity; then a per-project outlook."""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from findings.early_warning import doc_current
from findings.features import FEATURES_B, snapshot_frame, to_matrix
from findings.panel import add_months, latest, months, series

SEED = 0
MAX_MONTHS = 120
HGB_PARAMS = dict(loss="absolute_error", max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.15, random_state=SEED)


def _own_velocity(df, sector_median):
    v = df["velocity_pct_per_month"].copy()
    fill = df["sector"].astype(str).map(sector_median).astype(float)
    return v.fillna(fill).fillna(float(np.nanmedian(list(sector_median.values())) if sector_median else 0.0)).values


def run(panel, flags, frames, pair_list, test_pair="P4"):
    ids = [pid for pid, _, _ in pair_list]
    if test_pair not in frames:
        test_pair = ids[-1]
    before = ids[:ids.index(test_pair)]
    train_ids = [i for i in before if float(frames[i]["gap_months"].iloc[0]) == 1.0] or before
    tr = pd.concat([frames[i] for i in train_ids]).dropna(subset=["delta_prog"])
    te = frames[test_pair].dropna(subset=["delta_prog", "prog_t1"])
    y_tr = (tr["delta_prog"] / tr["gap_months"]).values
    sector_median = tr.assign(y=y_tr).groupby(tr["sector"].astype(str))["y"].median().to_dict()
    gap_te = te["gap_months"].values
    prog0 = te["physical_progress_pct"].fillna(0).values
    truth = te["prog_t1"].values
    preds = {"ZERO": prog0, "OWN_VELOCITY": np.clip(prog0 + _own_velocity(te, sector_median) * gap_te, 0, 100)}
    (Xtr, Xte), mask = to_matrix([tr, te], FEATURES_B)
    hgb = HistGradientBoostingRegressor(categorical_features=mask, **HGB_PARAMS).fit(Xtr, y_tr)
    preds["HGB"] = np.clip(prog0 + hgb.predict(Xte) * gap_te, 0, 100)
    results = []
    for mid, p in preds.items():
        err = np.abs(p - truth)
        results.append({"model_id": mid, "test_pair": test_pair, "n": int(len(err)), "mae": float(err.mean()), "median_ae": float(np.median(err))})
    winner = min(results, key=lambda r: (r["mae"], r["model_id"]))["model_id"]
    # outlook at the latest snapshot with the winning method
    last = latest(panel)
    lf = snapshot_frame(panel, last, flags, gap_months=1)
    ser = series(panel)
    allf = pd.concat([frames[i] for i in ids]).dropna(subset=["delta_prog"])
    per = {}
    prog = lf["physical_progress_pct"].fillna(0).values.copy()
    if winner == "HGB":
        (Xall, Xl), mask = to_matrix([allf, lf], FEATURES_B)
        model = HistGradientBoostingRegressor(categorical_features=mask, **HGB_PARAMS).fit(Xall, (allf["delta_prog"] / allf["gap_months"]).values)
        Xsim = Xl.copy()
    else:
        vel = _own_velocity(lf, sector_median)
    done = np.full(len(lf), -1)
    first = None
    for k in range(1, MAX_MONTHS + 1):
        if winner == "ZERO":
            break
        if winner == "HGB":
            Xsim["physical_progress_pct"] = prog
            Xsim["age_months"] = Xsim["age_months"] + 1
            Xsim["months_to_doc"] = Xsim["months_to_doc"] - 1
            delta = model.predict(Xsim)
        else:
            delta = vel
        if first is None:
            first = np.clip(prog + delta, 0, 100)
        prog = np.clip(prog + delta, 0, 100)
        newly = (done < 0) & (prog >= 100)
        done[newly] = k
        if (done >= 0).all():
            break
    for i, code in enumerate(lf.index):
        row = ser[code][-1]
        completion = add_months(last, int(done[i])) if done[i] > 0 else None
        doc = doc_current(row)
        per[code] = {"progress_next_pred": float(first[i]) if first is not None else float(prog[i]),
                     "expected_completion": completion,
                     "expected_delay_months": float(months(doc, completion)) if completion and doc else None}
    f3 = {f["project_code"] for f in flags if f["type"] in ("DOC_UNREACHABLE", "DOC_PASSED")}
    both = [c for c in per if c in f3 and per[c]["expected_delay_months"] is not None]
    agree = sum(1 for c in both if per[c]["expected_delay_months"] > 0)
    m2 = {"results": results, "winner": winner,
          "agreement_with_F3": {"n": len(both), "share_same_direction": (agree / len(both)) if both else None}}
    return m2, per
