"""The ONE feature builder. Every model imports from here. Features use only snapshots <= t0 (tested)."""
import math
from collections import defaultdict

import numpy as np
import pandas as pd

from findings.early_warning import doc_current, velocity
from findings.panel import ORDER, months, pairs_present, sector_map, series, snapshots_present

FEATURES_A = ["physical_progress_pct", "exp_share", "age_months", "months_to_doc", "log_cost_original", "cost_overrun_pct",
              "time_overrun_months", "has_revised_doc", "sector", "state", "gap_months"]
FEATURES_B = FEATURES_A + ["velocity_pct_per_month", "unreachable_ratio", "n_prior_revisions", "agency_prior_slip_rate",
                           "n_flags_to_t0", "exp_decrease_ever"]
CATEGORICAL = ["sector", "state"]
ARITH = {"EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL"}
NAN = float("nan")


def slip_labels(ser, t0, t1):
    out = {}
    for code, rs in ser.items():
        d = {r["snapshot"]: r for r in rs}
        if t0 in d and t1 in d:
            out[code] = int(d[t0]["doc_revised"] != d[t1]["doc_revised"])
    return out


def censored_exits(panel, t0, t1):
    ser = series(panel)
    a = {c for c, rs in ser.items() if any(r["snapshot"] == t0 for r in rs)}
    b = {c for c, rs in ser.items() if any(r["snapshot"] == t1 for r in rs)}
    return len(a - b)


def _upto(rs, t0):
    return [r for r in rs if ORDER[r["snapshot"]] <= ORDER[t0]]


def _ratio(rs_upto):
    # BUG (known, deliberately NOT fixed here): this `v <= 0` guard is the same denormal
    # hole that early_warning.assess() closed with ZERO_VELOCITY_EPS. np.polyfit on flat
    # progress returns ~1e-16 rather than exact 0.0, so that residue passes `v <= 0` and
    # the set-B feature `unreachable_ratio` can be ~1e17 where early_warning reports None.
    # The two therefore disagree on the same projects, by design of this note and not by
    # oversight. Fixing it changes the feature matrix and so re-fits M1/M2/M3/M4 and moves
    # every number in models.json and model_card.json; that is out of scope for a
    # presentation fix and is held for a change that can re-baseline the models properly.
    # Do not "tidy" this into ZERO_VELOCITY_EPS without regenerating and re-reviewing the
    # model outputs. HistGradientBoosting splits on rank, so a huge finite value behaves
    # like a large-value bucket; the logistic set-B model is the one this actually distorts.
    last = rs_upto[-1]
    prog, doc = last["physical_progress_pct"], doc_current(last)
    v = velocity(rs_upto)
    if prog is None or prog >= 100 or doc is None or v is None or v <= 0:
        return NAN
    rem = months(last["snapshot"], doc)
    return ((100 - prog) / v) / rem if rem > 0 else NAN


def _set_a(rs_upto, sector, gap):
    last = rs_upto[-1]
    t0 = last["snapshot"]
    prog, co, cr, exp = last["physical_progress_pct"], last["cost_original_cr"], last["cost_revised_cr"], last["expenditure_cum_cr"]
    doc = doc_current(last)
    return {
        "physical_progress_pct": NAN if prog is None else float(prog),
        "exp_share": exp / cr if exp is not None and cr else NAN,
        "age_months": float(months(last["approval_month"], t0)) if last["approval_month"] else NAN,
        "months_to_doc": float(months(t0, doc)) if doc else NAN,
        "log_cost_original": math.log(co + 1) if co is not None else NAN,
        "cost_overrun_pct": (cr - co) / co * 100 if co and cr is not None else NAN,
        "time_overrun_months": float(months(last["doc_original"], last["doc_revised"])) if last["doc_original"] and last["doc_revised"]
                               else (0.0 if last["doc_original"] else NAN),
        "has_revised_doc": 1.0 if last["doc_revised"] else 0.0,
        "sector": sector or "UNKNOWN", "state": last["state"] or "UNKNOWN", "gap_months": float(gap),
    }


def _history(panel, ser, t0, flags):
    """Per-code history features from pairs whose later month is <= t0 (strictly before the pair being built)."""
    earlier = [(a, b) for _, a, b in pairs_present(panel) if ORDER[b] <= ORDER[t0]]
    labels = [slip_labels(ser, a, b) for a, b in earlier]
    agency_of = {c: next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None) for c, rs in ser.items()}
    prior_revs, acc = defaultdict(int), defaultdict(list)
    for lab in labels:
        for c, y in lab.items():
            prior_revs[c] += y
            acc[agency_of[c]].append(y)
    agency_rate = {ag: sum(v) / len(v) for ag, v in acc.items()}
    nflags, expdec = defaultdict(int), defaultdict(int)
    for f in flags or []:
        if ORDER[f["to_snapshot"]] <= ORDER[t0]:
            if f["type"] in ARITH:
                nflags[f["project_code"]] += 1
            if f["type"] == "EXP_DECREASE":
                expdec[f["project_code"]] = 1

    def for_code(code, rs_upto):
        return {"velocity_pct_per_month": velocity(rs_upto) if velocity(rs_upto) is not None else NAN,
                "unreachable_ratio": _ratio(rs_upto),
                "n_prior_revisions": float(prior_revs[code]) if earlier else NAN,
                "agency_prior_slip_rate": agency_rate.get(agency_of[code], NAN) if earlier else NAN,
                "n_flags_to_t0": float(nflags[code]), "exp_decrease_ever": float(expdec[code])}
    return for_code


def _frame(rows_by_code):
    df = pd.DataFrame.from_dict(rows_by_code, orient="index")
    df.index.name = "project_code"
    for c in CATEGORICAL:
        df[c] = df[c].astype("category")
    return df


def pair_frame(panel, t0, t1, flags=None):
    ser, sectors = series(panel), sector_map(panel)
    gap = months(t0, t1)
    hist = _history(panel, ser, t0, flags)
    y = slip_labels(ser, t0, t1)
    rows = {}
    for code in sorted(y):
        rs = ser[code]
        up = _upto(rs, t0)
        r1 = next(r for r in rs if r["snapshot"] == t1)
        p0, p1 = up[-1]["physical_progress_pct"], r1["physical_progress_pct"]
        feat = {**_set_a(up, sectors.get(code), gap), **hist(code, up)}
        feat["y_slip"] = y[code]
        feat["delta_prog"] = (p1 - p0) if p0 is not None and p1 is not None else NAN
        feat["prog_t1"] = NAN if p1 is None else float(p1)
        rows[code] = feat
    return _frame(rows)[FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]]


def snapshot_frame(panel, t, flags=None, gap_months=1):
    ser, sectors = series(panel), sector_map(panel)
    hist = _history(panel, ser, t, flags)
    rows = {}
    for code, rs in ser.items():
        if not any(r["snapshot"] == t for r in rs):
            continue
        up = _upto(rs, t)
        rows[code] = {**_set_a(up, sectors.get(code), gap_months), **hist(code, up)}
    return _frame(rows)[FEATURES_B]


def to_matrix(frames, columns):
    """Categoricals -> integer codes using the FIRST frame's categories (unknown -> NaN); numerics unchanged."""
    cats = {c: list(frames[0][c].astype(str).unique()) for c in columns if c in CATEGORICAL}
    out = []
    for df in frames:
        m = df[columns].copy()
        for c, levels in cats.items():
            idx = {v: i for i, v in enumerate(levels)}
            m[c] = m[c].astype(str).map(idx).astype(float)
        out.append(m.astype(float))
    return out, [c in CATEGORICAL for c in columns]
