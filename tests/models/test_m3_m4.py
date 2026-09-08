from findings.contradictions import detect
from findings.models.m3_drivers import run as m3
from findings.models.m4_anomaly import run as m4


def test_m3_results_pdp_benchmark(synth):
    out, per = m3(synth, detect(synth))
    assert out["snapshot"] == "2026-07" and out["n"] > 400
    assert {(r["target"], r["model_id"]) for r in out["results"]} == {(t, m) for t in ["cost_overrun_pct", "time_overrun_months"] for m in ["OLS", "HGB"]}
    assert len(out["partial_dependence"]) == 6 and all(len(p["grid"]) == len(p["values"]) for p in out["partial_dependence"])
    assert out["sector_effects"] and any(c["target"] == "cost_overrun_pct" for c in out["coefficients_OLS"])
    p = next(iter(per.values()))
    assert set(p) == {"peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months"}


def test_m4_flags_about_two_percent(synth):
    out, per, flags = m4(synth)
    assert out["contamination"] == "auto" and out["n"] > 1000
    assert 0.01 <= len(out["flagged"]) / out["n"] <= 0.03
    assert all(f["type"] == "STAT_ANOMALY" and f["severity"] == "info" and f["sources"] for f in flags)
    assert any(p["anomaly_flag"] for p in per.values()) and all(p["anomaly_score"] is not None for p in per.values())
