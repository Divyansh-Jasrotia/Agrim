"""Outcome (i): the model card, generated from models.json so it can never drift from the numbers."""
from collections import Counter

from findings.features import FEATURES_A, FEATURES_B
from findings.panel import snapshots_present


def _pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}%"


def build(models, panel):
    m, counts = models["meta"], Counter(panel["snapshot"])
    test = m["test_pair"]
    res = {r["model_id"]: r for r in models["m1_slip"]["results"] if r["test_pair"] == test}
    sections = [
        {"title": "Data", "lines": [f"{len(snapshots_present(panel))} public MoSPI Flash Reports: " + ", ".join(f"{s} ({counts[s]} rows)" for s in snapshots_present(panel)),
                                    "Nine public fields per project; the Common Upload Form itself is behind role-based login and is not seen by any model."]},
        {"title": "Universe and censoring", "lines": [f"Pair {p['id']} ({p['from']} → {p['to']}, gap {p['gap_months']} months): n={p['n']}, positives={p['positives']}, exits excluded from labels={p['censored_exits']}" for p in m["pairs"]]},
        {"title": "Targets", "lines": ["M1: a revised completion date is filed in the next report (a reporting event, not a physical outcome).",
                                       "M2: next-month reported physical progress (points).",
                                       "M3: cross-sectional cost and time overrun on the latest report (drivers and peer benchmark, not a forecast).",
                                       "Cost escalation is not a forecast target: too few revision events in the window to train anything defensible."]},
        {"title": "Feature sets", "lines": ["A (public table fields): " + ", ".join(FEATURES_A), "B = A + audit-derived and history features: " + ", ".join(f for f in FEATURES_B if f not in FEATURES_A)]},
        {"title": "Validation", "lines": [f"Out-of-time: trained on {', '.join(m['train_pairs'])}, tested on {test}. No random splits. Label-shuffle control included.",
                                          f"random_state={m['random_state']}, OMP_NUM_THREADS={m['omp_threads']}, scikit-learn {m['sklearn_version']}."]},
        {"title": "M1 results on the held-out pair", "lines": [f"{mid}: PR-AUC {r['pr_auc']:.3f}, precision@100 {_pct(r['precision_at_100'])}, recall@100 {_pct(r['recall_at_100'])}, lift@100 {r['lift_at_100'] if r['lift_at_100'] is None else round(r['lift_at_100'], 2)} (n={r['n']}, positives={r['positives']}, base rate {_pct(r['base_rate'])})" for mid, r in res.items()]},
        {"title": "M2 results", "lines": [f"{r['model_id']}: MAE {r['mae']:.2f} points (median {r['median_ae']:.2f}, n={r['n']})" for r in models["m2_progress"]["results"]] + [f"Winner: {models['m2_progress']['winner']}"]},
        {"title": "M3 results (5-fold CV)", "lines": [f"{r['target']} / {r['model_id']}: R² {r['cv_r2']:.3f}, MAE {r['cv_mae']:.2f}" for r in models["m3_drivers"]["results"]]},
        {"title": "Known limitations", "lines": ["Labels are reporting events filtered through each agency's incentive to delay bad news.",
                                                 "The panel is survivor-selected: projects that leave are excluded from labels and counted above.",
                                                 "Nine fields; no milestones, contracts or site data. With PAIMANA access the same pipeline would consume the full CUF."]},
    ]
    return {"generated_at": m["generated_at"], "sections": sections}
