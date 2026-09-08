from findings.contradictions import detect
from findings.features import pair_frame
from findings.models.m2_progress import run
from findings.panel import pairs_present


def test_m2_baselines_winner_and_outlook(synth):
    flags = detect(synth)
    pairs = pairs_present(synth)
    frames = {pid: pair_frame(synth, a, b, flags) for pid, a, b in pairs}
    m2, per = run(synth, flags, frames, pairs, test_pair="P4")
    ids = {r["model_id"] for r in m2["results"]}
    assert ids == {"ZERO", "OWN_VELOCITY", "HGB"} and m2["winner"] in ids
    assert all(r["mae"] >= 0 and r["n"] > 0 for r in m2["results"])
    assert m2["agreement_with_F3"]["n"] >= 0
    code, p = next(iter(per.items()))
    assert set(p) == {"progress_next_pred", "expected_completion", "expected_delay_months"}
    done = [p for p in per.values() if p["expected_completion"]]
    assert done and all(len(p["expected_completion"]) == 7 for p in done)
    assert any(p["expected_delay_months"] is not None for p in per.values())
