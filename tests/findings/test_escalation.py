from findings.escalation import compute
from findings.panel import load_panel, sector_map

FIX = "contracts/fixtures/panel.sample.csv"


def test_rows_are_sorted_by_delay_rate_descending():
    panel = load_panel(FIX)
    out = compute(panel, sector_map(panel))
    rates = [(-(r["delay_rate_pct"] if r["delay_rate_pct"] is not None else -1), r["key"]) for r in out["rows"]]
    assert rates == sorted(rates)


def test_threshold_is_fifty_percent():
    panel = load_panel(FIX)
    assert compute(panel, sector_map(panel))["threshold_pct"] == 50.0


def test_escalate_requires_both_a_high_rate_and_no_improvement():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        if r["escalate"]:
            assert r["delay_rate_pct"] > 50.0
            assert r["improving"] is not True


def test_a_rollup_with_no_classifiable_projects_has_a_null_rate_and_is_not_escalated():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        if r["classifiable"] == 0:
            assert r["delay_rate_pct"] is None and r["escalate"] is False


def test_delayed_never_exceeds_classifiable():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        assert 0 <= r["delayed"] <= r["classifiable"] <= r["projects"]
