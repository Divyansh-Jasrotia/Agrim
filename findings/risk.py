"""F4: transparent rule-based risk score. v1 weights chosen for legibility, not fitted (say so on the slide). Never blended with M1."""
WEIGHTS = {("DOC_UNREACHABLE", "critical"): 40, ("DOC_UNREACHABLE", "high"): 25, ("DOC_UNREACHABLE", "medium"): 10,
           "DOC_PASSED": 25, "EXP_DECREASE": 20, "PROG_DECREASE": 15, "EXP_GT_REVISED_COST": 10,
           "ZERO_PROG_NONZERO_EXP": 5, "DOC_REVISED_FILED": 10, "COST_REVISED_FILED": 5}


def score(flags):
    total, reasons = 0, []
    for f in flags:
        w = WEIGHTS.get((f["type"], f["severity"]), WEIGHTS.get(f["type"], 0))
        if w:
            total += w
            reasons.append(f["detail"])
    s = min(100, total)
    band = "red" if s >= 60 else "amber" if s >= 30 else "green"
    return {"score": s, "band": band, "reasons": reasons}
