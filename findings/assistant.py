"""Eight fixed questions answered from the assembled findings with per-number provenance. No model, no network."""


def _top_risk(projects):
    ranked = sorted(projects, key=lambda p: (-p["risk"]["score"], p["project_code"]))
    return ranked[0] if ranked else None


def _fmt(x):
    return f"₹{x:,.2f} cr" if isinstance(x, (int, float)) else str(x)


def build(findings, projects, models=None):
    snaps = findings["meta"]["snapshots"]
    t0, t1 = (snaps[-2], snaps[-1]) if len(snaps) >= 2 else (snaps[0], snaps[0])
    by = {p["project_code"]: p for p in projects}
    out = []
    exp_rows = [r for r in findings["contradictions"]["rows"] if r["type"] == "EXP_DECREASE" and r["from_snapshot"] == t0 and r["to_snapshot"] == t1]
    out.append({"id": 1, "question": f"Which projects report cumulative expenditure falling between {t0} and {t1}?",
                "answer": (f"{len(exp_rows)} project(s). " + "; ".join(f"{r['project_code']} {r['project_name']}: {_fmt(r['before'])} → {_fmt(r['after'])} (page {r['sources'][-1]['page']})" for r in exp_rows[:5])) if exp_rows else f"None between {t0} and {t1}.",
                "sources": [s for r in exp_rows[:5] for s in r["sources"]]})
    ew = findings["early_warning"]["rows"]
    # A row with months_remaining <= 0 is the DOC_PASSED case: the stated date is already
    # behind us, which is a different statement from "too slow to get there in time".
    # Reporting the 1634 rows as one number contradicted the headline (1289) — I7.
    passed = [r for r in ew if r["months_remaining"] <= 0]
    unreach = [r for r in ew if r["months_remaining"] > 0]
    paced = sorted((r for r in unreach if r["ratio"] is not None), key=lambda r: (-r["ratio"], r["project_code"]))[:5]
    nopace = [r for r in unreach if r["ratio"] is None]
    out.append({"id": 2, "question": "Which projects cannot reach their stated completion date at their own reported pace?",
                "answer": (f"{len(unreach)} project(s) cannot reach the date they state at the pace they report"
                           + (f", of which {len(nopace)} report no usable pace at all (flat, backwards, or too slow to project a completion month)" if nopace else "")
                           + f". Separately, {len(passed)} project(s) are already past the completion date they state."
                           + ((" Worst five with a measurable pace: " + "; ".join(f"{r['project_code']} (needs {r['ratio']:.1f}x the time it has left)" for r in paced)) if paced else "")) if ew else "None flagged.",
                "sources": [s for r in unreach[:5] for s in r["sources"]]})
    pair = next((p for p in findings["exits"]["pairs"] if p["from"] == t0 and p["to"] == t1), None)
    ex_rows = [r for r in findings["exits"]["rows"] if r["last_seen"] == t0]
    parts = {}
    for r in ex_rows:
        parts[r["partition"]] = parts.get(r["partition"], 0) + 1
    out.append({"id": 3, "question": f"What left the monitored panel between {t0} and {t1}, and in what state?",
                "answer": (f"{pair['exited']} project(s) left and {pair['entered']} entered. Last observed progress of those that left: " + ", ".join(f"{k}: {v}" for k, v in sorted(parts.items())) + (f". The report prints {pair['commissioned_printed']} commissioned in {t1}." if pair.get("commissioned_printed") is not None else ". The report's commissioned count was not captured.")) if pair else "No pair available.",
                "sources": [s for r in ex_rows[:5] for s in r["sources"]]})
    st = sorted(findings["by_state"], key=lambda g: (-g["flagged"], g["key"]))
    out.append({"id": 4, "question": "Which state has the most flagged projects?",
                "answer": f"{st[0]['key']}: {st[0]['flagged']} of {st[0]['projects']} projects carry at least one flag." if st else "No state data.", "sources": []})
    fa = findings["field_audit"]
    # multiple_of_5_share / multiple_of_10_share are shares of ALL reported values, but
    # "about 20% and 10%" is the expectation among WHOLE numbers. Restate both on the
    # whole-number denominator so the observed and expected figures are comparable — C4.
    w = fa["whole_number_share"]
    m5 = fa["multiple_of_5_share"] / w if w else 0.0
    m10 = fa["multiple_of_10_share"] / w if w else 0.0
    out.append({"id": 5, "question": "How reliable is the Physical Progress field as filled?",
                "answer": f"In {fa['snapshot']}, {w:.0%} of reported progress values are whole numbers; a continuously measured percentage would show about 1%. "
                          f"Of those whole numbers, {m5:.0%} are multiples of 5 and {m10:.0%} are multiples of 10, against about 20% and 10% if their last digit carried information.", "sources": []})
    cov = findings["meta"]["coverage"]
    out.append({"id": 6, "question": "What share of the source reports did AGRIM parse?",
                "answer": "; ".join(f"{c['snapshot']}: {c['rows_parsed']} rows" + (f" of {c['rows_printed']} ({c['pct']}%)" if c["rows_printed"] else "") for c in cov), "sources": []})
    top = _top_risk(projects)
    if top:
        ml = top["ml"]
        mline = f" The model gives a {ml['slip_prob']:.0%} chance of a revised date being filed next report; top factor: {ml['slip_top_factors'][0]['feature']}." if ml and ml.get("slip_prob") is not None and ml.get("slip_top_factors") else " No model score is attached."
        out.append({"id": 7, "question": f"Why is project {top['project_code']} rated {top['risk']['band']}?",
                    "answer": f"Score {top['risk']['score']:.0f}. " + " ".join(top["risk"]["reasons"][:4]) + mline,
                    "sources": [s for f in top["flags"][:4] for s in f["sources"]]})
    else:
        out.append({"id": 7, "question": "Why is the top project rated as it is?", "answer": "No projects.", "sources": []})
    if models and models["m1_slip"]["results"]:
        res = {r["model_id"]: r for r in models["m1_slip"]["results"] if r["test_pair"] == models["meta"]["test_pair"]}
        hb, lr = res.get("HGB_B"), res.get("LR_A")
        out.append({"id": 8, "question": "Did the model beat the conventional method on the held-out report?",
                    "answer": (f"On pair {models['meta']['test_pair']} (n={hb['n']}, positives={hb['positives']}), gradient boosting with audit features recalled {hb['recall_at_100']:.0%} of the projects that filed a revised date in its top 100 (precision {hb['precision_at_100']:.0%}); logistic regression recalled {lr['recall_at_100']:.0%} (precision {lr['precision_at_100']:.0%}). " + ("The ML model wins." if hb["pr_auc"] > lr["pr_auc"] else "The conventional model wins on PR-AUC; we show it.")) if hb and lr else "Model results incomplete.",
                    "sources": []})
    else:
        out.append({"id": 8, "question": "Did the model beat the conventional method on the held-out report?", "answer": "Models were not run in this build.", "sources": []})
    return out
