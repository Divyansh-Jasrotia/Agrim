import json
from pathlib import Path

import pytest

from parser.run import parse_snapshot

PDF = Path("data/pdfs/Flash_Report_April_2026.pdf")


@pytest.mark.skipif(not PDF.exists(), reason="April PDF not fetched")
def test_april_parses_at_least_90_percent_and_sums_match():
    rows = parse_snapshot("2026-04")
    agg = json.loads(Path("data/aggregates.json").read_text(encoding="utf-8"))["2026-04"]
    assert len(rows) >= 0.90 * agg["rows_printed"], f"only {len(rows)} rows"
    for k in ["cost_original_cr", "cost_revised_cr", "expenditure_cum_cr"]:
        s = sum(r[k] for r in rows if r[k] is not None)
        assert abs(s - agg[k]) / agg[k] < 0.005, f"{k}: parsed {s:,.0f} vs printed {agg[k]:,.0f}"
    codes = [r["project_code"] for r in rows if r["project_code"]]
    assert len(codes) == len(set(codes)), "duplicate project codes in one snapshot"
