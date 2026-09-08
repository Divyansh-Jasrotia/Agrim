"""M1: will this project file a revised completion date in the next report? Out-of-time validation; baseline always shown."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from findings.features import CATEGORICAL, FEATURES_A, FEATURES_B, censored_exits, snapshot_frame, to_matrix
from findings.models.metrics import summarize
from findings.panel import latest, months

SEED = 0
HGB = dict(max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.15, class_weight="balanced", random_state=SEED)


def fit_hgb(X, y, cat_mask):
    return HistGradientBoostingClassifier(categorical_features=cat_mask, **HGB).fit(X, y)


def fit_lr(df, y):
    cats = [c for c in df.columns if c in CATEGORICAL]
    nums = [c for c in df.columns if c not in CATEGORICAL]
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cats),
                              ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), nums)])
    pipe = Pipeline([("prep", prep), ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=SEED))])
    return pipe.fit(df.assign(**{c: df[c].astype(str) for c in cats}), y)


def _lr_frame(df):
    return df[FEATURES_A].assign(**{c: df[c].astype(str) for c in CATEGORICAL})


def _shap_factors(model, X, raw, k=5):
    try:
        import shap
        sv = shap.TreeExplainer(model).shap_values(X.values)
        if isinstance(sv, list):
            sv = sv[-1]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[..., -1]
    except Exception:  # SHAP unavailable or unsupported: fall back to zero contributions, still deterministic
        sv = np.zeros(X.shape)
    factors = {}
    for i, code in enumerate(X.index):
        order = np.argsort(-np.abs(sv[i]), kind="stable")[:k]
        fs = []
        for j in order:
            col = X.columns[j]
            val = raw.loc[code, col]
            if isinstance(val, float) and np.isnan(val):
                val = None
            elif not isinstance(val, (int, float, str)):
                val = str(val)
            fs.append({"feature": col, "contribution": float(sv[i, j]), "value": val})
        factors[code] = fs
    return factors


def run(panel, flags, frames, pair_list, test_pair="P4"):
    ids = [pid for pid, _, _ in pair_list]
    if test_pair not in frames:
        test_pair = ids[-1]
    train_ids = ids[:ids.index(test_pair)]
    if not train_ids:
        raise SystemExit("M1 needs at least one training pair before the test pair")
    evaluations = [(train_ids, test_pair)]
    if len(train_ids) >= 2:
        evaluations.append((train_ids[:-1], train_ids[-1]))
    results, keep = [], {}
    for tr_ids, te in evaluations:
        tr = pd.concat([frames[i] for i in tr_ids])
        te_df = frames[te]
        y_tr, y_te = tr["y_slip"].values.astype(int), te_df["y_slip"].values.astype(int)
        if y_tr.sum() == 0 or y_te.sum() == 0:
            continue
        lr = fit_lr(_lr_frame(tr), y_tr)
        results.append(summarize("LR_A", te, y_te, lr.predict_proba(_lr_frame(te_df))[:, 1]))
        for mid, cols in [("HGB_A", FEATURES_A), ("HGB_B", FEATURES_B)]:
            (Xtr, Xte), mask = to_matrix([tr, te_df], cols)
            m = fit_hgb(Xtr, y_tr, mask)
            results.append(summarize(mid, te, y_te, m.predict_proba(Xte)[:, 1]))
            if mid == "HGB_B" and te == test_pair:
                keep = {"model": m, "Xte": Xte, "y_te": y_te, "lr": lr}
                ys = np.random.RandomState(SEED).permutation(y_tr)
                results.append(summarize("HGB_B_SHUFFLED", te, y_te, fit_hgb(Xtr, ys, mask).predict_proba(Xte)[:, 1]))
    if not keep:
        raise SystemExit(f"M1: no positives in test pair {test_pair}; cannot evaluate")
    imp = permutation_importance(keep["model"], keep["Xte"], keep["y_te"], scoring="average_precision", n_repeats=10, random_state=SEED)
    importance = sorted([{"feature": f, "mean": float(m), "std": float(s)} for f, m, s in zip(FEATURES_B, imp.importances_mean, imp.importances_std)],
                        key=lambda d: (-d["mean"], d["feature"]))
    names = keep["lr"].named_steps["prep"].get_feature_names_out()
    coefs = [{"feature": str(n), "value": float(c)} for n, c in zip(names, keep["lr"].named_steps["clf"].coef_[0])]
    allf = pd.concat([frames[i] for i in ids])
    last = latest(panel)
    latest_frame = snapshot_frame(panel, last, flags, gap_months=1)
    (Xall, Xlatest), mask = to_matrix([allf, latest_frame], FEATURES_B)
    final = fit_hgb(Xall, allf["y_slip"].values.astype(int), mask)
    probs = final.predict_proba(Xlatest)[:, 1]
    order = sorted(range(len(probs)), key=lambda i: (-probs[i], latest_frame.index[i]))
    rank = {latest_frame.index[i]: r + 1 for r, i in enumerate(order)}
    factors = _shap_factors(final, Xlatest, latest_frame)
    per_project = {code: {"slip_prob": float(probs[i]), "slip_rank": rank[code], "slip_top_factors": factors[code]}
                   for i, code in enumerate(latest_frame.index)}
    watch = [{"project_code": c, "slip_prob": per_project[c]["slip_prob"], "slip_rank": per_project[c]["slip_rank"]}
             for c in sorted(per_project, key=lambda c: per_project[c]["slip_rank"])[:100]]
    pairs_meta = [{"id": pid, "from": a, "to": b, "gap_months": months(a, b), "n": int(len(frames[pid])),
                   "positives": int(frames[pid]["y_slip"].sum()), "censored_exits": censored_exits(panel, a, b)} for pid, a, b in pair_list]
    m1 = {"feature_sets": {"A": FEATURES_A, "B": FEATURES_B}, "results": results, "importance_HGB_B": importance,
          "coefficients_LR_A": coefs, "watchlist": watch}
    return m1, per_project, pairs_meta
