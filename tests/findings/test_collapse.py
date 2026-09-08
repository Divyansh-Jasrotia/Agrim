from findings.collapse import collapse
from findings.contradictions import detect
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def _f(code, typ, a, b, sources):
    return {"project_code": code, "type": typ, "severity": "low", "from_snapshot": a,
            "to_snapshot": b, "before": 0.0, "after": 1.0, "detail": f"{typ} in {b}.",
            "sources": sources}


def test_consecutive_same_type_flags_merge_into_one():
    flags = [_f("A", "T", None, "2026-04", [{"snapshot": "2026-04", "page": 1}]),
             _f("A", "T", None, "2026-05", [{"snapshot": "2026-05", "page": 2}]),
             _f("A", "T", None, "2026-06", [{"snapshot": "2026-06", "page": 3}])]
    out = collapse(flags)
    assert len(out) == 1
    assert out[0]["first_snapshot"] == "2026-04"
    assert out[0]["to_snapshot"] == "2026-06"
    assert out[0]["occurrences"] == 3


def test_no_page_citation_is_ever_lost():
    flags = [_f("A", "T", None, "2026-04", [{"snapshot": "2026-04", "page": 1}]),
             _f("A", "T", None, "2026-05", [{"snapshot": "2026-05", "page": 2}])]
    out = collapse(flags)
    assert out[0]["sources"] == [{"snapshot": "2026-04", "page": 1}, {"snapshot": "2026-05", "page": 2}]


def test_different_types_and_projects_never_merge():
    flags = [_f("A", "T1", None, "2026-04", [{"snapshot": "2026-04", "page": 1}]),
             _f("A", "T2", None, "2026-04", [{"snapshot": "2026-04", "page": 1}]),
             _f("B", "T1", None, "2026-04", [{"snapshot": "2026-04", "page": 1}])]
    assert len(collapse(flags)) == 3


def test_a_single_flag_is_unchanged_apart_from_the_new_keys():
    one = _f("A", "T", None, "2026-04", [{"snapshot": "2026-04", "page": 1}])
    out = collapse([one])[0]
    assert out["occurrences"] == 1 and out["first_snapshot"] == "2026-04"
    assert out["detail"] == one["detail"] and out["after"] == one["after"]


def test_collapse_on_the_real_fixture_reduces_the_planted_repeats():
    raw = detect(load_panel(FIX))
    out = collapse(raw)
    zero = [f for f in out if f["project_code"] == "100005" and f["type"] == "ZERO_PROG_NONZERO_EXP"]
    assert len(zero) == 1 and zero[0]["occurrences"] == 5
    assert len(zero[0]["sources"]) == 5
    doc = [f for f in out if f["project_code"] == "100011" and f["type"] == "DOC_BEFORE_APPROVAL"]
    assert len(doc) == 1 and doc[0]["occurrences"] == 5


def test_output_is_sorted_like_detect():
    out = collapse(detect(load_panel(FIX)))
    assert out == sorted(out, key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
