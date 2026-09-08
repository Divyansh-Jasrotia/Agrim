import pytest

from findings.early_warning import MAX_PROJECTION_MONTHS, assess, compute, velocity
from findings.panel import load_panel, series

FIX = "contracts/fixtures/panel.sample.csv"


def test_velocity_is_ols_slope_in_points_per_month():
    rows = [{"snapshot": "2025-12", "physical_progress_pct": 20.0}, {"snapshot": "2026-04", "physical_progress_pct": 28.0},
            {"snapshot": "2026-07", "physical_progress_pct": 34.0}]
    assert velocity(rows) == pytest.approx(2.0, abs=0.05)
    assert velocity(rows[:1]) is None


def test_assess_classes():
    ser = series(load_panel(FIX))
    a = assess(ser["100005"])
    assert a["type"] == "DOC_PASSED" and a["months_remaining"] < 0
    b = assess(ser["100006"])
    assert b["type"] == "DOC_UNREACHABLE" and b["severity"] == "critical" and b["ratio"] > 2
    assert assess(ser["100001"]) is None      # reachable at its own pace
    assert assess(ser["100011"]) is None      # already >= 100


def test_assess_flat_progress_denormal_slope_is_unreachable_not_astronomical_ratio():
    # Regression for BUGFIX-EW: identical progress across snapshots makes the true
    # slope 0, but np.polyfit returns a floating-point denormal (e.g. ~1e-16) instead
    # of an exact zero. That tiny positive residue must not slip past the zero-pace
    # guard in assess() and produce a ~1e17 ratio.
    rows = [
        {"snapshot": "2025-12", "physical_progress_pct": 20.0, "doc_original": "2027-01", "doc_revised": None},
        {"snapshot": "2026-04", "physical_progress_pct": 20.0, "doc_original": "2027-01", "doc_revised": None},
        {"snapshot": "2026-07", "physical_progress_pct": 20.0, "doc_original": "2027-01", "doc_revised": None},
    ]
    v = velocity(rows)
    assert v is not None and 0 < v < 5e-5  # confirm this is the denormal case, not exact 0.0
    a = assess(rows)
    assert a is not None
    assert a["type"] == "DOC_UNREACHABLE"
    assert a["ratio"] is None
    assert a["months_needed"] is None


def test_compute_rows_and_flags():
    out = compute(load_panel(FIX))
    codes = {r["project_code"] for r in out["rows"]}
    assert "100006" in codes and "100001" not in codes
    ratios = [r["ratio"] for r in out["rows"] if r["ratio"] is not None]
    assert ratios == sorted(ratios, reverse=True)
    f = [x for x in out["flags"] if x["project_code"] == "100006"][0]
    assert f["type"] == "DOC_UNREACHABLE" and f["to_snapshot"] == "2026-07" and f["from_snapshot"] == "2025-12"
    assert "needs" in f["detail"] and "leaves" in f["detail"]


def _rows(progress, doc="2027-01"):
    snaps = ["2025-12", "2026-04", "2026-07"]
    return [{"snapshot": s, "physical_progress_pct": p, "doc_original": doc, "doc_revised": None} for s, p in zip(snaps, progress)]


def test_assess_negative_velocity_says_progress_went_backwards_not_no_progress():
    # BUGFIX-EW-NEG: a negative slope used to fall into the `v < ZERO_VELOCITY_EPS`
    # branch and be described as "No reported progress", contradicting the negative
    # pace printed beside it in the table. Progress going backwards is a stronger
    # statement and must be worded as such.
    a = assess(_rows([40.0, 35.0, 30.0]))
    assert a is not None and a["type"] == "DOC_UNREACHABLE" and a["severity"] == "critical"
    assert a["velocity"] < 0
    assert "backwards" in a["detail"]
    assert "No reported progress" not in a["detail"]
    assert a["months_needed"] is None and a["ratio"] is None


def test_assess_zero_velocity_still_says_no_reported_progress():
    a = assess(_rows([20.0, 20.0, 20.0]))
    assert a is not None and a["detail"].startswith("No reported progress")
    assert a["months_needed"] is None and a["ratio"] is None


def test_assess_beyond_horizon_projection_is_collapsed_not_printed_as_precise():
    # BUGFIX-EW-HORIZON: a pace of ~0.001 pt/month divides out to tens of thousands of
    # months (5,400 years for project 615191). The finding stands; the fabricated
    # precision does not. Past MAX_PROJECTION_MONTHS no figure is projected.
    a = assess(_rows([20.0, 20.007, 20.015], doc="2029-03"))
    assert a is not None and a["type"] == "DOC_UNREACHABLE" and a["severity"] == "critical"
    assert 0 < a["velocity"] < 0.01
    assert a["months_needed"] is None and a["ratio"] is None
    assert "no meaningful completion month" in a["detail"]


def test_assess_inside_horizon_still_projects_a_number():
    a = assess(_rows([10.0, 12.0, 14.0], doc="2027-01"))
    assert a is not None and a["type"] == "DOC_UNREACHABLE"
    assert a["months_needed"] is not None and a["months_needed"] <= MAX_PROJECTION_MONTHS
    assert a["ratio"] is not None and "needs" in a["detail"]


def test_assess_negative_denormal_slope_is_flat_not_backwards(monkeypatch):
    # np.polyfit on flat progress returns a denormal of EITHER sign. A slope of -1e-16 is
    # a floating-point residue, not a project reporting progress in reverse, so the
    # backwards branch is bounded at -ZERO_VELOCITY_EPS rather than at 0.
    import findings.early_warning as ew
    monkeypatch.setattr(ew, "velocity", lambda rows: -1e-16)
    a = ew.assess(_rows([20.0, 20.0, 20.0]))
    assert a is not None and a["detail"].startswith("No reported progress")
    assert "backwards" not in a["detail"]


def test_assess_real_decline_below_minus_eps_is_backwards(monkeypatch):
    import findings.early_warning as ew
    monkeypatch.setattr(ew, "velocity", lambda rows: -0.0666)
    a = ew.assess(_rows([20.0, 20.0, 20.0]))
    assert a is not None and "moved backwards" in a["detail"]
