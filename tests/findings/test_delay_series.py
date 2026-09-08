from findings.delay_series import classify, compute
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def test_no_original_date_is_not_classifiable():
    assert classify(None, None, "2026-07") is None
    assert classify(None, "2027-01", "2026-07") is None


def test_revised_date_measures_against_the_original():
    assert classify("2026-01", "2026-07", "2026-07") == 6
    assert classify("2026-01", "2031-01", "2026-07") == 60


def test_unrevised_but_overdue_measures_against_the_snapshot():
    assert classify("2026-01", None, "2026-07") == 6


def test_unrevised_and_not_yet_due_is_on_schedule():
    assert classify("2027-01", None, "2026-07") == 0


def test_a_revised_date_earlier_than_the_original_is_on_schedule():
    assert classify("2026-07", "2026-01", "2026-07") == -6


def test_bands_partition_every_classifiable_project():
    out = compute(load_panel(FIX))
    for row in out["rows"]:
        total = row["on_schedule"] + row["d_1_12"] + row["d_13_24"] + row["d_25_60"] + row["d_61_plus"]
        assert total == row["classifiable"]


def test_every_snapshot_in_the_panel_gets_a_row():
    panel = load_panel(FIX)
    out = compute(panel)
    assert [r["snapshot"] for r in out["rows"]] == sorted(set(panel["snapshot"]), key=lambda s: (s[:4], s[5:]))


def test_null_doc_is_counted_not_dropped():
    out = compute(load_panel(FIX))
    for row in out["rows"]:
        assert row["doc_null"] >= 0
        assert isinstance(row["doc_null"], int)
