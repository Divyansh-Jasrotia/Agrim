from findings.contradictions import detect
from findings.disclosure_lag import compute as lag
from findings.early_warning import compute as ew
from findings.field_audit import compute as fields
from findings.panel import load_panel
from findings.risk import score

FIX = "contracts/fixtures/panel.sample.csv"


def flags_for(code):
    panel = load_panel(FIX)
    allf = detect(panel) + ew(panel)["flags"]
    return [f for f in allf if f["project_code"] == code]


def test_risk_weights_bands_and_reasons():
    r5 = score(flags_for("100005"))          # 5 x ZERO_PROG (5 each) + DOC_PASSED (25) = 50
    assert r5["score"] == 50 and r5["band"] == "amber" and len(r5["reasons"]) == 6
    r2 = score(flags_for("100002"))          # EXP_DECREASE 20 + DOC_UNREACHABLE critical 40 = 60
    assert r2["score"] == 60 and r2["band"] == "red"
    assert score([]) == {"score": 0, "band": "green", "reasons": []}
    assert score(flags_for("100005") * 3)["score"] == 100


def test_field_audit_shapes():
    fa = fields(load_panel(FIX))
    assert fa["snapshot"] == "2026-07"
    assert sum(d["count"] for d in fa["terminal_digit"]) == 10 and [d["digit"] for d in fa["terminal_digit"]] == list(range(10))
    assert fa["whole_number_share"] == 1.0 and 0 <= fa["multiple_of_5_share"] <= 1
    assert fa["staleness_by_agency"] == []   # no agency has 5 projects in the fixture


def test_disclosure_lag_backcasts_100006():
    out = lag(load_panel(FIX))
    assert out["status"] == "computed"
    rows = {r["project_code"]: r for r in out["rows"]}
    assert rows["100006"]["filed_at"] == "2026-05" and rows["100006"]["first_unreachable"] == "2026-04" and rows["100006"]["lag_months"] == 1
    assert out["median_lag_months"] == 1
