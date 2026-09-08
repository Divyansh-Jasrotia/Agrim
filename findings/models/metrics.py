"""Ranking metrics for an officer's decision: which 100 projects to review this month. No accuracy, ever."""
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score


def _order(s):
    return np.argsort(-np.asarray(s), kind="stable")


def precision_at_k(y, s, k=100):
    top = np.asarray(y)[_order(s)[:k]]
    return float(top.mean()) if len(top) else 0.0


def recall_at_k(y, s, k=100):
    y = np.asarray(y)
    pos = y.sum()
    return float(y[_order(s)[:k]].sum() / pos) if pos else 0.0


def calibration(y, s, bins=10):
    y, s = np.asarray(y), np.asarray(s)
    edges = np.linspace(0, 1, bins + 1)
    out = []
    for i in range(bins):
        m = (s >= edges[i]) & ((s < edges[i + 1]) if i < bins - 1 else (s <= edges[i + 1]))
        out.append({"bin": i, "mean_pred": float(s[m].mean()) if m.any() else None,
                    "mean_obs": float(y[m].mean()) if m.any() else None, "n": int(m.sum())})
    return out


def pr_curve_points(y, s, n=50):
    p, r, _ = precision_recall_curve(y, s)
    idx = np.linspace(0, len(p) - 1, min(n, len(p))).astype(int)
    return [{"x": float(r[i]), "y": float(p[i])} for i in idx]


def summarize(model_id, test_pair, y, s):
    y, s = np.asarray(y).astype(int), np.asarray(s, dtype=float)
    positives, n = int(y.sum()), int(len(y))
    base = positives / n if n else 0.0
    p100 = precision_at_k(y, s)
    return {"model_id": model_id, "test_pair": test_pair, "n": n, "positives": positives, "base_rate": base,
            "pr_auc": float(average_precision_score(y, s)) if 0 < positives < n else 0.0,
            "roc_auc": float(roc_auc_score(y, s)) if 0 < positives < n else None,
            "precision_at_100": p100, "recall_at_100": recall_at_k(y, s),
            "lift_at_100": (p100 / base) if base else None,
            "calibration": calibration(y, s), "pr_curve": pr_curve_points(y, s) if 0 < positives < n else []}
