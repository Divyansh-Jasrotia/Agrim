import csv
import json
from collections import Counter
from pathlib import Path

import pytest

PANEL = Path("data/out/panel.csv")


@pytest.mark.skipif(not PANEL.exists(), reason="panel.csv not built")
def test_panel_covers_five_snapshots_at_95_percent():
    agg = json.loads(Path("data/aggregates.json").read_text(encoding="utf-8"))
    with open(PANEL, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts = Counter(r["snapshot"] for r in rows)
    assert set(counts) == {"2025-12", "2026-04", "2026-05", "2026-06", "2026-07"}
    for snap, n in counts.items():
        printed = (agg.get(snap) or {}).get("rows_printed")
        assert printed, f"record rows_printed for {snap} in data/aggregates.json"
        assert n >= 0.95 * printed, f"{snap}: {n} of {printed} ({100 * n / printed:.1f}%)"
    for snap in counts:
        codes = [r["project_code"] for r in rows if r["snapshot"] == snap and r["project_code"]]
        assert len(codes) == len(set(codes)), f"duplicate codes in {snap}"
