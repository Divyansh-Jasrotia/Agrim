"""M3: what drives cost and time overrun across the panel (OLS vs gradient boosting) and how each project compares with its peers."""
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import partial_dependence
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from findings.features import snapshot_frame, to_matrix
from findings.panel import latest, series

SEED = 0
FEATS = ["log_cost_original", "age_months", "physical_progress_pct", "approval_year", "agency_size", "sector", "state"]
CATS = ["sector", "state"]
PDP_FEATS = ["log_cost_original", "age_months", "physical_progress_pct"]
TARGETS = {"cost_overrun_pct": (-50, 500), "time_overrun_months": (0, 240)}


def frame(panel, flags):
    last = latest(panel)
    sf = snapshot_frame(panel, last, flags)
    ser = series(panel)
    rows_last = {c: rs[-1] for c, rs in ser.items() if rs[-1]["snapshot"] == last}
    agency = {c: r["agency_raw"] for c, r in rows_last.items()}
    size = Counter(a for a in agency.values() if a)
    df = sf.copy()
    df["approval_year"] = [float(rows_last[c]["approval_month"][:4]) if rows_last[c]["approval_month"] else np.nan for c in df.index]
    df["agency_size"] = [float(size.get(agency[c], 0)) for c in df.index]
    for t, (lo, hi) in TARGETS.items():
        df[t] = df[t].clip(lo, hi)
    return df[df["log_cost_original"].notna()]


def _ols():
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CATS),
                              ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), [f for f in FEATS if f not in CATS])])
    return Pipeline([("prep", prep), ("reg", LinearRegression())])


def _str_cats(df):
    return df[FEATS].assign(**{c: df[c].astype(str) for c in CATS})


def run(panel, flags):
    df = frame(panel, flags)
    kf = KFold(5, shuffle=True, random_state=SEED)
    results, pdps, coefs, per = [], [], [], {c: {} for c in df.index}
    sector_eff = {}
    for target in TARGETS:
        d = df.dropna(subset=[target])
        y = d[target].values
        Xs = _str_cats(d)
        ols = _ols()
        results.append({"target": target, "model_id": "OLS", "cv_r2": float(cross_val_score(ols, Xs, y, cv=kf, scoring="r2").mean()),
                        "cv_mae": float(-cross_val_score(ols, Xs, y, cv=kf, scoring="neg_mean_absolute_error").mean())})
        ols.fit(Xs, y)
        names = ols.named_steps["prep"].get_feature_names_out()
        for n, c in zip(names, ols.named_steps["reg"].coef_):
            coefs.append({"target": target, "feature": str(n), "coef": float(c)})
            if str(n).startswith("cat__sector_"):
                sector_eff.setdefault(str(n)[len("cat__sector_"):], {})[target] = float(c)
        (X,), mask = to_matrix([d], FEATS)
        hgb = HistGradientBoostingRegressor(categorical_features=mask, random_state=SEED)
        results.append({"target": target, "model_id": "HGB", "cv_r2": float(cross_val_score(hgb, X, y, cv=kf, scoring="r2").mean()),
                        "cv_mae": float(-cross_val_score(hgb, X, y, cv=kf, scoring="neg_mean_absolute_error").mean())})
        expected = cross_val_predict(hgb, X, y, cv=kf)
        hgb.fit(X, y)
        for f in PDP_FEATS:
            pd_res = partial_dependence(hgb, X, [FEATS.index(f)], grid_resolution=20, kind="average")
            grid = pd_res["grid_values"][0] if "grid_values" in pd_res else pd_res["values"][0]
            pdps.append({"target": target, "feature": f, "grid": [float(g) for g in grid], "values": [float(v) for v in pd_res["average"][0]]})
        key_e, key_r = ("peer_expected_cost_overrun_pct", "cost_overrun_residual_pct") if target == "cost_overrun_pct" else ("peer_expected_time_overrun_months", "time_overrun_residual_months")
        for code, e, a in zip(d.index, expected, y):
            per[code][key_e], per[code][key_r] = float(e), float(a - e)
    for code in per:
        for k in ["peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months"]:
            per[code].setdefault(k, None)
    counts = Counter(df["sector"].astype(str))
    effects = [{"sector": s, "effect_cost_pct": v.get("cost_overrun_pct", 0.0), "effect_time_months": v.get("time_overrun_months", 0.0), "n": int(counts.get(s, 0))}
               for s, v in sorted(sector_eff.items())]
    return {"snapshot": latest(panel), "n": int(len(df)), "results": results, "partial_dependence": pdps,
            "sector_effects": effects, "coefficients_OLS": coefs}, per
