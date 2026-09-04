from findings.exits import compute
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def test_exits_and_entries_per_pair():
    ex = compute(load_panel(FIX), aggregates={"2026-05": {"commissioned": 9}})
    pairs = {(p["from"], p["to"]): p for p in ex["pairs"]}
    assert pairs[("2026-04", "2026-05")]["exited"] == 1 and pairs[("2026-04", "2026-05")]["commissioned_printed"] == 9
    assert pairs[("2026-05", "2026-06")]["exited"] == 1 and pairs[("2026-05", "2026-06")]["entered"] == 1
    assert pairs[("2026-06", "2026-07")]["exited"] == 0 and pairs[("2026-06", "2026-07")]["commissioned_printed"] is None
    rows = {r["project_code"]: r for r in ex["rows"]}
    assert rows["100008"]["partition"] == "LAST_SEEN_LT_50" and rows["100008"]["last_seen"] == "2026-04"
    assert rows["100007"]["partition"] == "LAST_SEEN_GE_95" and rows["100007"]["last_progress_pct"] == 97.0
    assert rows["100007"]["sources"] == [{"snapshot": "2026-05", "page": 57}]
    assert ex["status"]["100008"] == ("exited", "2025-12", "2026-04")
    assert ex["status"]["100009"] == ("ongoing", "2026-06", "2026-07")
