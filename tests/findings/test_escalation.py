from findings.escalation import compute
from findings.panel import load_panel, sector_map

FIX = "contracts/fixtures/panel.sample.csv"
NEWLINE = chr(10)


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


HEADER = ("snapshot,source_file,source_sha256,page,sl_no,project_code,legacy_ocms_code,pmgid,project_name,"
          "agency_raw,table_section,state,approval_month,start_month,doc_original,doc_revised,cost_original_cr,"
          "cost_revised_cr,expenditure_cum_cr,physical_progress_pct,parse_flags")


def _row(snapshot, sl, code, section, doc_original):
    """sector_map keys off table_section when the PDF printed section headers, so that is the rollup."""
    return (f"{snapshot},f.pdf,{'a' * 64},1,{sl},{code},,,P{code},Agency,{section},State,01/2020,01/2020,"
            f"{doc_original},,100,100,50,10,")


def test_a_rollup_with_no_classifiable_projects_has_a_null_rate_and_is_not_escalated(tmp_path):
    """A rollup whose every project lacks a date must report null, never 0%.

    No rollup in the committed fixture has classifiable == 0, so the original form of this
    test never executed its assertion. This builds the case instead.
    """
    csv = tmp_path / "panel.csv"
    rows = [_row("2026-06", 1, "1", "Dated", "2020-01"), _row("2026-07", 2, "1", "Dated", "2020-01"),
            _row("2026-06", 3, "2", "Dateless", ""), _row("2026-07", 4, "2", "Dateless", "")]
    csv.write_text(NEWLINE.join([HEADER] + rows) + NEWLINE, encoding="utf-8")
    panel = load_panel(str(csv))
    by_key = {r["key"]: r for r in compute(panel, sector_map(panel))["rows"]}
    dateless = [r for r in by_key.values() if r["classifiable"] == 0]
    assert len(dateless) == 1, f"expected one dateless rollup, got {list(by_key)}"
    assert dateless[0]["delay_rate_pct"] is None
    assert dateless[0]["first_rate_pct"] is None
    assert dateless[0]["escalate"] is False


def test_delayed_never_exceeds_classifiable():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        assert 0 <= r["delayed"] <= r["classifiable"] <= r["projects"]
