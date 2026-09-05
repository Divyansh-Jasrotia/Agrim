import math

import pandas as pd

from findings.contradictions import detect
from findings.features import CATEGORICAL, FEATURES_A, FEATURES_B, censored_exits, pair_frame, slip_labels, snapshot_frame, to_matrix
from findings.panel import load_panel, series

FIX = "contracts/fixtures/panel.sample.csv"


def test_labels_and_shapes_on_fixture():
    panel = load_panel(FIX)
    y = slip_labels(series(panel), "2026-04", "2026-05")
    assert y["100006"] == 1 and y["100001"] == 0 and "100008" not in y      # 100008 exits after April
    df = pair_frame(panel, "2026-04", "2026-05", detect(panel))
    assert list(df.columns) == FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]
    assert df.loc["100006", "y_slip"] == 1 and df.loc["100006", "gap_months"] == 1.0
    assert df.loc["100002", "exp_decrease_ever"] == 0.0      # the drop happens in May, after t0 = April
    assert math.isnan(df.loc["100001", "agency_prior_slip_rate"]) is False   # P1 exists before April
    p1 = pair_frame(panel, "2025-12", "2026-04")
    assert all(math.isnan(v) for v in p1["agency_prior_slip_rate"]) and all(math.isnan(v) for v in p1["n_prior_revisions"])
    assert censored_exits(panel, "2026-04", "2026-05") == 1


def test_snapshot_frame_and_matrix(synth):
    sf = snapshot_frame(synth, "2026-07")
    assert list(sf.columns) == FEATURES_B and len(sf) > 400
    (m,), mask = to_matrix([sf], FEATURES_B)
    assert mask == [c in CATEGORICAL for c in FEATURES_B]
    assert m.dtypes.map(lambda d: d.kind).isin(["f", "i"]).all()


def test_no_feature_uses_the_later_month(synth):
    base = pair_frame(synth, "2026-06", "2026-07")
    mutated = synth.copy()
    m = mutated["snapshot"] == "2026-07"
    mutated.loc[m, "physical_progress_pct"] = 0.0
    mutated.loc[m, "expenditure_cum_cr"] = 0.0
    mutated.loc[m, "doc_revised"] = "2099-01"
    mutated.loc[m, "cost_revised_cr"] = 1.0
    after = pair_frame(mutated, "2026-06", "2026-07")
    pd.testing.assert_frame_equal(base[FEATURES_B], after[FEATURES_B])
    assert (base["y_slip"] != after["y_slip"]).any()
