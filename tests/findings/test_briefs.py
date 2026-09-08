import copy
import json

from findings.briefs import brief_for, fact_sheet, grounded, numbers_in, template_brief
import findings.briefs as briefs_module

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


# --- Fix round 1 regression tests -------------------------------------------------

def test_fact_sheet_negative_cost_overrun_renders_as_below_with_positive_magnitude():
    # Finding 1: project 400151 has cost_overrun_residual_pct = -6.3402 (it BEAT its
    # peer cohort), but the old hardcoded "... above comparable projects" wording made
    # the fact sheet self-contradictory ("cost overrun -6.34 percentage points above").
    p = copy.deepcopy(PROJECT)
    p["ml"] = {"cost_overrun_residual_pct": -6.3402, "slip_prob": None, "slip_rank": None,
               "expected_completion": None, "expected_delay_months": None}
    sheet = fact_sheet(p)
    assert "6.3402 percentage points below comparable projects" in sheet or "6.34" in sheet
    assert "below comparable projects" in sheet
    assert "-6.34" not in sheet
    assert "above comparable projects" not in sheet


def test_fact_sheet_positive_cost_overrun_still_renders_as_above():
    p = copy.deepcopy(PROJECT)
    p["ml"] = {"cost_overrun_residual_pct": 11.5, "slip_prob": None, "slip_rank": None,
               "expected_completion": None, "expected_delay_months": None}
    sheet = fact_sheet(p)
    assert "above comparable projects" in sheet
    assert "below comparable projects" not in sheet


def test_brief_for_fallback_records_model_as_template(monkeypatch):
    # Finding 2: projects 400116 and 617214 exhausted all 3 attempts and fell back to
    # template_brief(), but the returned record still said "model": "qwen2.5:3b" even
    # though the LLM never produced the text that shipped. The fallback branch must
    # attribute the brief to "template", matching the --template-only path.
    monkeypatch.setattr(briefs_module, "_ollama_generate", lambda model, prompt: "an invented number 999999 not in the facts")
    result = brief_for(PROJECT, "qwen2.5:3b")
    assert result["grounded"] is False
    assert result["attempts"] == 3
    assert result["model"] == "template"
    assert result["brief"] == template_brief(PROJECT)


def test_grounded_rejects_project_code_quoted_as_a_quantity():
    # Finding 3: fact_sheet() injects the project code into its first line, so its
    # digits land in the allowed-number set. Project 705410's published brief exploited
    # this to claim "a distance of 705410 meters" -- a fabricated measurement -- and
    # still passed grounded() because 705410 is the project's own code, not a distance.
    facts = fact_sheet(PROJECT)
    code = PROJECT["project_code"]
    assert not grounded(f"The project covers a distance of {code} meters.", facts)
    # A brief that only cites real fact-sheet quantities must still be grounded.
    assert grounded("Expenditure fell from ₹620.00 cr to ₹120.00 cr while progress rose from 64% to 66%.", facts)


def test_grounded_rejects_source_page_number_quoted_as_a_quantity():
    # Same laundering bug, different identifier: a source-document page number is not a
    # measurement about the project either, and must not license a numeric claim.
    facts = fact_sheet(PROJECT)
    page = PROJECT["snapshots"][0]["page"]
    assert not grounded(f"The project affects {page} villages.", facts)
