from collections import Counter

from findings.delay_series import _band, classify, compute
from findings.panel import load_panel, series

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


def test_band_edges_match_the_april_2014_report():
    """The published bands are 1-12, 13-24, 25-60, 61+. Pin every edge."""
    assert _band(-6) == "on_schedule"
    assert _band(0) == "on_schedule"
    assert _band(1) == "d_1_12"
    assert _band(12) == "d_1_12"
    assert _band(13) == "d_13_24"
    assert _band(24) == "d_13_24"
    assert _band(25) == "d_25_60"
    assert _band(60) == "d_25_60"
    assert _band(61) == "d_61_plus"


def test_no_project_is_lost_between_the_bands_and_doc_null():
    """classifiable + doc_null must account for every row in the snapshot.

    compute() defines classifiable as the sum of the bands, so comparing the two proves
    nothing. Comparing against the panel's own row count does.
    """
    panel = load_panel(FIX)
    out = compute(panel)
    per_snapshot = Counter(r["snapshot"] for rs in series(panel).values() for r in rs)
    for row in out["rows"]:
        assert row["classifiable"] + row["doc_null"] == per_snapshot[row["snapshot"]]


def test_every_snapshot_in_the_panel_gets_a_row():
    panel = load_panel(FIX)
    out = compute(panel)
    assert [r["snapshot"] for r in out["rows"]] == sorted(set(panel["snapshot"]), key=lambda s: (s[:4], s[5:]))


HEADER = ("snapshot,source_file,source_sha256,page,sl_no,project_code,legacy_ocms_code,pmgid,project_name,"
          "agency_raw,table_section,state,approval_month,start_month,doc_original,doc_revised,cost_original_cr,"
          "cost_revised_cr,expenditure_cum_cr,physical_progress_pct,parse_flags")


def _row(code, doc_original):
    return (f"2026-07,f.pdf,{'a' * 64},1,{code},{code},,,P{code},Agency,Sec,State,01/2020,01/2020,"
            f"{doc_original},,100,100,50,10,")


def test_a_project_with_no_original_date_lands_in_doc_null(tmp_path):
    """A missing date must never be silently bucketed as on schedule (AGENTS.md rule 3).

    The committed fixture has no such row, so this builds one.
    """
    csv = tmp_path / "panel.csv"
    lines = [HEADER, _row("1", "2020-01"), _row("2", "")]
    csv.write_text("\n".join(lines) + "\n", encoding="utf-8")
    row = compute(load_panel(str(csv)))["rows"][0]
    assert row["doc_null"] == 1
    assert row["classifiable"] == 1
    assert row["d_61_plus"] == 1
    assert row["on_schedule"] == 0
