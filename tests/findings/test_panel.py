from findings.panel import add_months, latest, load_panel, months, pairs_present, sector_map, series, snapshots_present

FIX = "contracts/fixtures/panel.sample.csv"


def test_months_and_add_months():
    assert months("2025-12", "2026-04") == 4
    assert months("2026-07", "2026-07") == 0
    assert months("2026-07", "2026-03") == -4
    assert add_months("2025-12", 1) == "2026-01"
    assert add_months("2026-07", 11) == "2027-06"


def test_load_and_series():
    panel = load_panel(FIX)
    assert len(panel) == 52
    assert panel["expenditure_cum_cr"].dtype.kind == "f"
    ser = series(panel)
    assert len(ser) == 12
    assert [r["snapshot"] for r in ser["100007"]] == ["2025-12", "2026-04", "2026-05"]
    assert ser["100012"][0]["snapshot"] == "2026-04"  # the Dec row has no code and is excluded
    assert ser["100001"][0]["doc_revised"] is None and ser["100001"][0]["pmgid"] is None


def test_snapshots_pairs_latest_sector():
    panel = load_panel(FIX)
    assert snapshots_present(panel) == ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
    assert latest(panel) == "2026-07"
    assert pairs_present(panel) == [("P1", "2025-12", "2026-04"), ("P2", "2026-04", "2026-05"), ("P3", "2026-05", "2026-06"), ("P4", "2026-06", "2026-07")]
    assert sector_map(panel)["100001"] == "Road Transport and Highways"
