import pytest

from findings.early_warning import assess, compute, velocity
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
