"""F1: arithmetic contradictions within and between consecutive reports. Deterministic; no thresholds beyond the spec."""
from findings.panel import series, source


def _flag(code, typ, sev, a, b, before, after, detail, sources):
    return {"project_code": code, "type": typ, "severity": sev, "from_snapshot": a, "to_snapshot": b,
            "before": before, "after": after, "detail": detail, "sources": sources}


def _cr(x):
    return f"₹{x:,.2f} cr"


def detect(panel):
    flags = []
    for code, rs in series(panel).items():
        for r in rs:
            s, exp, cr, prog = r["snapshot"], r["expenditure_cum_cr"], r["cost_revised_cr"], r["physical_progress_pct"]
            src = [source(r)]
            if exp is not None and cr is not None and exp > cr + 0.005:
                flags.append(_flag(code, "EXP_GT_REVISED_COST", "medium", None, s, cr, exp,
                                   f"Cumulative expenditure {_cr(exp)} exceeds the revised cost {_cr(cr)} in {s}.", src))
            if prog is not None and prog == 0 and exp is not None and exp > 0:
                flags.append(_flag(code, "ZERO_PROG_NONZERO_EXP", "low", None, s, prog, exp,
                                   f"Physical progress is 0% while cumulative expenditure is {_cr(exp)} in {s}.", src))
            if prog is not None and prog > 100:
                flags.append(_flag(code, "PROG_GT_100", "medium", None, s, None, prog,
                                   f"Physical progress is reported as {prog:g}% in {s}.", src))
            if r["doc_original"] and r["approval_month"] and r["doc_original"] < r["approval_month"]:
                flags.append(_flag(code, "DOC_BEFORE_APPROVAL", "low", None, s, r["approval_month"], r["doc_original"],
                                   f"Original completion date {r['doc_original']} is before the approval month {r['approval_month']} in {s}.", src))
        for a, b in zip(rs, rs[1:]):
            sa, sb, src = a["snapshot"], b["snapshot"], [source(a), source(b)]
            ea, eb = a["expenditure_cum_cr"], b["expenditure_cum_cr"]
            if ea is not None and eb is not None and eb < ea - 0.01:
                sev = "critical" if (ea - eb) >= 0.10 * ea else "high"
                flags.append(_flag(code, "EXP_DECREASE", sev, sa, sb, ea, eb,
                                   f"Cumulative expenditure falls from {_cr(ea)} in {sa} to {_cr(eb)} in {sb}; a cumulative field cannot decrease.", src))
            pa, pb = a["physical_progress_pct"], b["physical_progress_pct"]
            if pa is not None and pb is not None and pb < pa - 0.01:
                sev = "high" if (pa - pb) >= 5 else "medium"
                flags.append(_flag(code, "PROG_DECREASE", sev, sa, sb, pa, pb,
                                   f"Physical progress falls from {pa:g}% in {sa} to {pb:g}% in {sb}.", src))
            if a["doc_revised"] != b["doc_revised"]:
                flags.append(_flag(code, "DOC_REVISED_FILED", "info", sa, sb, a["doc_revised"], b["doc_revised"],
                                   f"Revised completion date changed from {a['doc_revised'] or 'none'} to {b['doc_revised'] or 'none'} between {sa} and {sb}.", src))
            ca, cb = a["cost_revised_cr"], b["cost_revised_cr"]
            if ca != cb and not (ca is None and cb is None):
                flags.append(_flag(code, "COST_REVISED_FILED", "info", sa, sb, ca, cb,
                                   f"Revised cost changed from {_cr(ca) if ca is not None else 'none'} to {_cr(cb) if cb is not None else 'none'} between {sa} and {sb}.", src))
    flags.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return flags
