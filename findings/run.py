"""Assemble every JSON the dashboard reads. Usage:
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json [--no-models]"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")  # before any sklearn import (Task 14)
import argparse
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from findings import assistant, contradictions, disclosure_lag, early_warning, exits, field_audit, risk
from findings.panel import latest, load_panel, sector_map, series, snapshots_present, source

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VERSION = "1.0.0"
ARITH = {"EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL"}
from findings.models import pipeline  # noqa: E402  (after OMP_NUM_THREADS is set)
run_models = pipeline.run


def _round(x):
    if isinstance(x, dict):
        return {k: _round(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_round(v) for v in x]
    if isinstance(x, float):
        return None if math.isnan(x) or math.isinf(x) else round(x, 4)
    return x


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_round(obj), sort_keys=True, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def generated_at():
    return os.environ.get("AGRIM_GENERATED_AT") or datetime.now(timezone.utc).isoformat(timespec="seconds")


def _strip(flag):
    return {k: v for k, v in flag.items() if k != "project_code"}


def build_projects(panel, flags, status, sectors, ml_by_code):
    by_code = {}
    for f in flags:
        by_code.setdefault(f["project_code"], []).append(f)
    projects = []
    for code, rs in series(panel).items():
        fl = by_code.get(code, [])
        projects.append({"project_code": code, "project_name": rs[-1]["project_name"],
                         "agency_raw": next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None),
                         "state": next((r["state"] for r in reversed(rs) if r["state"]), None), "sector": sectors.get(code),
                         "status": status[code][0], "first_seen": status[code][1], "last_seen": status[code][2],
                         "snapshots": [{"snapshot": r["snapshot"], "page": r["page"], "doc_original": r["doc_original"], "doc_revised": r["doc_revised"],
                                        "cost_original_cr": r["cost_original_cr"], "cost_revised_cr": r["cost_revised_cr"],
                                        "expenditure_cum_cr": r["expenditure_cum_cr"], "physical_progress_pct": r["physical_progress_pct"]} for r in rs],
                         "flags": [_strip(f) for f in fl], "risk": risk.score(fl), "ml": (ml_by_code or {}).get(code)})
    return projects


def build_findings(panel, projects, flags, ex, ew, aggregates, models):
    last = latest(panel)
    counts = Counter(panel["snapshot"])
    coverage = []
    for s in snapshots_present(panel):
        printed = ((aggregates or {}).get(s) or {}).get("rows_printed")
        coverage.append({"snapshot": s, "rows_parsed": int(counts[s]), "rows_printed": printed, "pct": round(100 * counts[s] / printed, 2) if printed else None})
    latest_rows = [p["snapshots"][-1] for p in projects if p["last_seen"] == last]
    cost_rev = sum(r["cost_revised_cr"] or 0 for r in latest_rows)
    overrun = sum((r["cost_revised_cr"] - r["cost_original_cr"]) for r in latest_rows if r["cost_revised_cr"] is not None and r["cost_original_cr"] is not None)
    c_rows = [f for f in flags if f["type"] in ARITH or f["type"] == "STAT_ANOMALY"]
    # The ledger shows both, but the headline counts only the rule-based arithmetic
    # contradictions. STAT_ANOMALY rows come from the M4 isolation forest; counting them
    # as "arithmetic impossibilities" would blend F4-style rule output with model output,
    # which is exactly what this project says it never does. The model count stays
    # visible and separate as contradictions.by_type[STAT_ANOMALY] — C2.
    rule_rows = [f for f in c_rows if f["type"] in ARITH]
    by = {p["project_code"]: p for p in projects}
    contradiction_rows = [{"project_code": f["project_code"], "project_name": by[f["project_code"]]["project_name"], **_strip(f)} for f in c_rows]
    by_type = Counter(f["type"] for f in c_rows)
    groups = {"state": {}, "sector": {}}
    for p in projects:
        if p["last_seen"] != last:
            continue
        for kind, key in [("state", p["state"] or "UNKNOWN"), ("sector", p["sector"] or "UNKNOWN")]:
            g = groups[kind].setdefault(key, {"key": key, "projects": 0, "flagged": 0, "red": 0})
            g["projects"] += 1
            g["flagged"] += 1 if any(f["severity"] != "info" for f in p["flags"]) else 0
            g["red"] += 1 if p["risk"]["band"] == "red" else 0
    watch = {w["project_code"] for w in models["m1_slip"]["watchlist"]} if models else set()
    review = []
    for p in projects:
        if p["last_seen"] != last:
            continue
        if not (any(f["severity"] != "info" for f in p["flags"]) or p["project_code"] in watch):
            continue
        ml = p["ml"] or {}
        review.append({"project_code": p["project_code"], "project_name": p["project_name"], "state": p["state"], "sector": p["sector"],
                       "risk_band": p["risk"]["band"], "risk_score": p["risk"]["score"], "slip_prob": ml.get("slip_prob"),
                       "expected_delay_months": ml.get("expected_delay_months"),
                       "flag_types": ";".join(sorted({f["type"] for f in p["flags"] if f["severity"] != "info"})), "page": p["snapshots"][-1]["page"]})
    review.sort(key=lambda r: (-r["risk_score"], r["project_code"]))
    findings = {
        "meta": {"contract_version": CONTRACT_VERSION, "generated_at": generated_at(), "snapshots": snapshots_present(panel), "coverage": coverage,
                 "headline": {"projects_latest": len(latest_rows), "cost_revised_total_cr": round(cost_rev, 2), "overrun_total_cr": round(overrun, 2),
                              "contradictions_total": len(rule_rows), "exits_total": sum(p["exited"] for p in ex["pairs"]),
                              "unreachable_total": sum(1 for f in flags if f["type"] == "DOC_UNREACHABLE"), "watchlist_size": len(watch)}},
        "contradictions": {"by_type": [{"type": t, "count": n} for t, n in sorted(by_type.items())], "rows": contradiction_rows},
        "exits": {"pairs": ex["pairs"], "rows": ex["rows"]},
        "early_warning": {"rows": ew["rows"]},
        "field_audit": field_audit.compute(panel),
        "disclosure_lag": disclosure_lag.compute(panel),
        "by_state": sorted(groups["state"].values(), key=lambda g: g["key"]),
        "by_sector": sorted(groups["sector"].values(), key=lambda g: g["key"]),
        "review_pack": review,
        "assistant": [],
    }
    findings["assistant"] = assistant.build(findings, projects, models)
    return findings


def build(panel, aggregates, with_models):
    flags = contradictions.detect(panel)
    ew = early_warning.compute(panel)
    flags = sorted(flags + ew["flags"], key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    ex = exits.compute(panel, aggregates)
    sectors = sector_map(panel)
    models = model_card = ml_by_code = None
    if with_models:
        if run_models is None:
            raise SystemExit("models are not wired yet (Task 14); run with --no-models")
        models, ml_by_code, extra_flags, model_card = run_models(panel, flags, sectors)
        flags = sorted(flags + extra_flags, key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    projects = build_projects(panel, flags, ex["status"], sectors, ml_by_code)
    findings = build_findings(panel, projects, flags, ex, ew, aggregates, models)
    return projects, findings, models, model_card


def deck_numbers(findings, models):
    h = findings["meta"]["headline"]
    nums = {"projects_latest": h["projects_latest"], "cost_revised_total_cr": h["cost_revised_total_cr"], "overrun_total_cr": h["overrun_total_cr"],
            "contradictions_total": h["contradictions_total"], "exits_total": h["exits_total"], "unreachable_total": h["unreachable_total"],
            "latest_snapshot": findings["meta"]["snapshots"][-1], "first_snapshot": findings["meta"]["snapshots"][0]}
    for c in findings["meta"]["coverage"]:
        if c["pct"] is not None:
            nums[f"coverage_pct_{c['snapshot']}"] = c["pct"]
    for t in findings["contradictions"]["by_type"]:
        nums[f"count_{t['type']}"] = t["count"]
    drops = [r for r in findings["contradictions"]["rows"] if r["type"] == "EXP_DECREASE"
             and isinstance(r["before"], (int, float)) and isinstance(r["after"], (int, float))]
    if drops:
        top = max(drops, key=lambda r: (r["before"] - r["after"], r["project_code"]))
        nums["opener_code"], nums["opener_before_cr"], nums["opener_after_cr"] = top["project_code"], top["before"], top["after"]
    if models:
        for r in models["m1_slip"]["results"]:
            if r["test_pair"] == models["meta"]["test_pair"]:
                for k in ["pr_auc", "precision_at_100", "recall_at_100", "positives", "n"]:
                    nums[f"m1_{r['model_id']}_{k}"] = r[k]
        for r in models["m2_progress"]["results"]:
            nums[f"m2_{r['model_id']}_mae"] = r["mae"]
    return nums


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(ROOT / "data" / "out" / "panel.csv"))
    ap.add_argument("--out", default=str(ROOT / "web" / "public" / "data"))
    ap.add_argument("--deck", default=None)
    ap.add_argument("--aggregates", default=str(ROOT / "data" / "aggregates.json"))
    ap.add_argument("--no-models", action="store_true")
    a = ap.parse_args(argv)
    aggregates = json.loads(Path(a.aggregates).read_text(encoding="utf-8")) if Path(a.aggregates).exists() else {}
    panel = load_panel(a.panel)
    projects, findings, models, model_card = build(panel, aggregates, with_models=not a.no_models)
    out = Path(a.out)
    write_json(out / "projects.json", projects)
    write_json(out / "findings.json", findings)
    if models is not None:
        write_json(out / "models.json", models)
        write_json(out / "model_card.json", model_card)
    if a.deck:
        write_json(a.deck, deck_numbers(findings, models))
    h = findings["meta"]["headline"]
    print(f"wrote {out}: {len(projects)} projects, {h['contradictions_total']} rule-based contradictions, {h['exits_total']} exits, {h['unreachable_total']} unreachable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
