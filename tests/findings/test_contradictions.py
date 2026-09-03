from findings.contradictions import detect
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def by(flags, code, typ):
    return [f for f in flags if f["project_code"] == code and f["type"] == typ]


def test_every_planted_contradiction_is_found():
    flags = detect(load_panel(FIX))
    f = by(flags, "100002", "EXP_DECREASE")
    assert len(f) == 1 and f[0]["severity"] == "critical" and (f[0]["from_snapshot"], f[0]["to_snapshot"]) == ("2026-04", "2026-05")
    assert f[0]["before"] == 620.0 and f[0]["after"] == 120.0 and f[0]["sources"] == [{"snapshot": "2026-04", "page": 56}, {"snapshot": "2026-05", "page": 57}]
    g = by(flags, "100003", "PROG_DECREASE")
    assert len(g) == 1 and g[0]["severity"] == "high" and g[0]["to_snapshot"] == "2026-06"
    assert {x["to_snapshot"] for x in by(flags, "100004", "EXP_GT_REVISED_COST")} == {"2026-06", "2026-07"}
    assert len(by(flags, "100005", "ZERO_PROG_NONZERO_EXP")) == 5
    assert len(by(flags, "100011", "PROG_GT_100")) == 1 and len(by(flags, "100011", "DOC_BEFORE_APPROVAL")) == 5
    d = by(flags, "100006", "DOC_REVISED_FILED")
    assert len(d) == 1 and d[0]["before"] == "2026-12" and d[0]["after"] == "2027-06" and d[0]["severity"] == "info"
    c = by(flags, "100010", "COST_REVISED_FILED")
    assert len(c) == 1 and c[0]["before"] == 800.0 and c[0]["after"] == 1600.0
    assert not [x for x in flags if x["project_code"] == "100001"]


def test_flags_are_sorted_and_have_required_keys():
    flags = detect(load_panel(FIX))
    keys = {"project_code", "type", "severity", "from_snapshot", "to_snapshot", "before", "after", "detail", "sources"}
    assert all(set(f) == keys for f in flags)
    assert flags == sorted(flags, key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
