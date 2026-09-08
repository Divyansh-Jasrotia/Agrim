import json

from findings.briefs import fact_sheet, grounded, numbers_in, template_brief

PROJECT = json.loads("""{"project_code": "100002", "project_name": "Hydro Power Station Unit 2", "agency_raw": "NHPC", "state": "Himachal Pradesh",
 "sector": "Power", "status": "ongoing", "first_seen": "2025-12", "last_seen": "2026-07",
 "snapshots": [{"snapshot": "2026-04", "page": 56, "doc_original": "2026-12", "doc_revised": null, "cost_original_cr": 900.0, "cost_revised_cr": 950.0, "expenditure_cum_cr": 620.0, "physical_progress_pct": 64.0},
               {"snapshot": "2026-05", "page": 57, "doc_original": "2026-12", "doc_revised": null, "cost_original_cr": 900.0, "cost_revised_cr": 950.0, "expenditure_cum_cr": 120.0, "physical_progress_pct": 66.0}],
 "flags": [{"type": "EXP_DECREASE", "severity": "critical", "from_snapshot": "2026-04", "to_snapshot": "2026-05", "before": 620.0, "after": 120.0,
            "detail": "Cumulative expenditure falls from ₹620.00 cr in 2026-04 to ₹120.00 cr in 2026-05; a cumulative field cannot decrease.", "sources": [{"snapshot": "2026-04", "page": 56}, {"snapshot": "2026-05", "page": 57}]}],
 "risk": {"score": 60, "band": "red", "reasons": ["Cumulative expenditure falls from ₹620.00 cr in 2026-04 to ₹120.00 cr in 2026-05; a cumulative field cannot decrease."]},
 "ml": null}""")


def test_numbers_in_normalises_commas_and_rupees():
    assert numbers_in("₹53,629.73 cr became ₹401.84 cr; progress 92% → 97%") == {"53629.73", "401.84", "92", "97"}


def test_grounded_rejects_invented_numbers():
    facts = fact_sheet(PROJECT)
    assert grounded("Expenditure fell from ₹620.00 cr to ₹120.00 cr while progress rose from 64% to 66%.", facts)
    assert not grounded("Expenditure fell by ₹500 cr, about 81% of the earlier figure.", facts)   # 81 is not in the facts


def test_template_brief_is_grounded_by_construction():
    assert grounded(template_brief(PROJECT), fact_sheet(PROJECT))
