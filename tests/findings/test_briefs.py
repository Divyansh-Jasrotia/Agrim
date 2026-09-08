import copy
import json

from findings.briefs import brief_for, fact_sheet, grounded, numbers_in, template_brief, _mask_identifiers
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

    # Strengthened (fix round 2): the fixture above has no identifier/quantity collision,
    # so it never exercised the identifier-masking logic in grounded() at all -- it would
    # pass even with a naive check. Give a snapshot a page number equal to a genuine
    # quantity template_brief() actually cites (the risk score, 60) and confirm the
    # invariant still holds for a colliding project too.
    p = copy.deepcopy(PROJECT)
    p["snapshots"][0]["page"] = 60  # collides with PROJECT["risk"]["score"] == 60
    assert grounded(template_brief(p), fact_sheet(p))


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
    # This assertion was hardcoded to `is False` before fix round 3, which coincidentally
    # matched the pre-fix bug this same branch had (see
    # test_brief_for_exhausted_attempts_records_real_grounded_result below). Now that
    # brief_for() calls grounded() on the shipped text instead of hardcoding False, this
    # fixture's template_brief() output -- which is groundable by construction -- must be
    # reported as grounded here too.
    assert result["grounded"] == grounded(template_brief(PROJECT), fact_sheet(PROJECT))
    assert result["grounded"] is True
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


# --- Fix round 2 regression tests -------------------------------------------------
#
# Finding A: the fix-round-1 grounded() was `numbers_in(facts) - _identifier_numbers(facts)`
# -- it subtracted identifier VALUES from the whole allowed set, so if an identifier's
# value happened to equal a genuine quantity elsewhere in the fact sheet, that legitimate
# quantity was banned everywhere in the brief, not just at the identifier's own position.
# Confirmed real: project 705454's page 85 collided with a genuine progress figure of 85,
# rejecting a true "progress of 85% in its most recent report" sentence; template_brief()
# itself failed grounded() for 91 of 2128 projects (e.g. 400120: page 70 collided with its
# own risk score of 70). The fix must exclude identifiers POSITIONALLY (mask the identifier
# substrings out of the fact-sheet text, then compute numbers_in() over the masked text),
# not by value.

def test_grounded_identifier_masking_is_positional_not_by_value():
    # Explicit, self-contained collision fixture (does not depend on which real project
    # happens to collide): give a snapshot a page number equal to a genuine fact-sheet
    # quantity that has nothing to do with pages -- the risk score, which is 60 in PROJECT.
    p = copy.deepcopy(PROJECT)
    p["snapshots"][0]["page"] = 60
    facts = fact_sheet(p)

    # Requirement 1 (the collision case): 60 is independently a real quantity (the risk
    # score) even though it also happens to be a page number somewhere else in the sheet.
    # A brief citing it as the risk score must be grounded -- masking is positional, so the
    # page-number occurrence of "60" does not blank out the risk-score occurrence of "60".
    assert grounded("The rule-based risk score is 60.", facts)

    # Requirement 2 (do not regress the original fix): a value that is ONLY an identifier
    # and never a genuine quantity anywhere in the sheet must still be rejected. The
    # project code (100002) does not collide with anything in this fixture.
    code = p["project_code"]
    assert not grounded(f"The project covers a distance of {code} meters.", facts)

    # And the page identifier itself, quoted for something it never measured, must still
    # be rejected purely by virtue of being masked at its own position -- it only survives
    # above because 60 is *also* the risk score, not because page numbers are allowed.
    assert not grounded("The project affects 999999 villages.", facts)


def test_grounded_masking_does_not_corrupt_neighbouring_numbers():
    # A masking implementation that deletes matched substrings (instead of same-length
    # replacement) risks splicing digits on either side of a removed identifier into a new,
    # unintended number. Construct a fact sheet where a real quantity sits immediately
    # next to the masked project-code region and confirm it survives untouched.
    p = copy.deepcopy(PROJECT)
    p["project_code"] = "42"
    p["project_name"] = "9 Village Lift Irrigation Scheme"  # "9" sits right after "42:" once masked
    facts = fact_sheet(p)
    assert facts.startswith("Project 42: 9 Village")
    # "9" is a real, present number (the start of the project name / not itself a claimed
    # quantity, but numbers_in() tokenises it) -- it must not have merged with the masked
    # "42" into something like "429" nor vanished from the masked text.
    masked = _mask_identifiers(facts)
    assert len(masked) == len(facts)       # same-length replacement: no join/shift possible
    assert "429" not in numbers_in(masked)
    assert "42" not in numbers_in(masked)  # the identifier itself is gone
    assert "9" in numbers_in(masked)       # the neighbouring number is untouched


def test_brief_for_template_only_records_real_grounded_result(monkeypatch):
    # Finding B: brief_for(..., template_only=True) returned "grounded": True
    # unconditionally, without ever calling grounded(). That was harmless while
    # template_brief() was trivially grounded, but after Finding A's fix it is not: the
    # --template-only path must call grounded() on the template text and record the real
    # result, like every other path -- never special-cased to always pass.
    facts = fact_sheet(PROJECT)

    # Positive control: the real template_brief() output, and the recorded value must
    # match an independent call to grounded() -- not just happen to be True.
    real = brief_for(PROJECT, "qwen2.5:3b", template_only=True)
    assert real["model"] == "template"
    assert real["attempts"] == 0
    assert real["grounded"] == grounded(template_brief(PROJECT), facts)
    assert real["grounded"] is True

    # Proof it is actually computed, not hardcoded: force template_brief() to emit a
    # number that is not in the facts and confirm the record honestly reports False.
    monkeypatch.setattr(briefs_module, "template_brief",
                         lambda proj: "An invented distance of 999999 meters appears here.")
    fabricated = brief_for(PROJECT, "qwen2.5:3b", template_only=True)
    assert fabricated["model"] == "template"
    assert fabricated["grounded"] is False


# --- Fix round 3 regression test --------------------------------------------------

def test_brief_for_exhausted_attempts_records_real_grounded_result(monkeypatch):
    # Finding: after exhausting all 3 LLM attempts, brief_for() ships template_brief(p)
    # text but hardcoded "grounded": False without ever calling grounded() on it. That was
    # roughly harmless while template_brief() often failed grounding, but the round-2 fix
    # that made template_brief() grounded-by-construction for real projects (see
    # test_template_brief_grounded_for_all_real_projects) turned this into a false negative
    # almost every time this branch fires. The final fallback must call grounded() on the
    # text it actually ships, exactly like the --template-only branch already does -- and
    # the "model" field must stay "template" regardless, since template text is what is
    # actually shipped (provenance and verification are separate facts).
    monkeypatch.setattr(briefs_module, "_ollama_generate", lambda model, prompt: "an invented number 999999 not in the facts")

    # Positive control: template_brief(PROJECT) is groundable (see
    # test_template_brief_is_grounded_by_construction above), so the record must say so --
    # not just happen to be True, but match an independent call to grounded().
    result = brief_for(PROJECT, "qwen2.5:3b")
    assert result["attempts"] == 3
    assert result["model"] == "template"
    assert result["grounded"] == grounded(template_brief(PROJECT), fact_sheet(PROJECT))
    assert result["grounded"] is True

    # Negative control, constructed explicitly (not relying on a real project happening to
    # fail grounding): force template_brief() itself to emit a number absent from the
    # facts, so the exhausted-attempts branch must honestly report False rather than True.
    monkeypatch.setattr(briefs_module, "template_brief",
                         lambda proj: "An invented distance of 999999 meters appears here.")
    fabricated = brief_for(PROJECT, "qwen2.5:3b")
    assert fabricated["attempts"] == 3
    assert fabricated["model"] == "template"
    assert fabricated["grounded"] is False


# --- Invariant: template_brief() is grounded for a broad sample of real projects --------

def test_template_brief_grounded_for_all_real_projects():
    # This is the invariant the round-2 fix exists to restore: template_brief() only ever
    # string-formats fields already present in fact_sheet(), so it should be grounded by
    # construction for essentially every real project, not just hand-built fixtures. A
    # previous (by-value) identifier exclusion silently broke this for 91 of 2128 real
    # projects. Running it over the full real projects.json means this invariant cannot
    # silently rot again -- a regression here fails the suite, not just a demo.
    projects = json.loads((briefs_module.DATA / "projects.json").read_text(encoding="utf-8"))
    ungrounded = [p["project_code"] for p in projects if not grounded(template_brief(p), fact_sheet(p))]
    assert ungrounded == [], (
        f"template_brief() is not grounded for {len(ungrounded)} of {len(projects)} real projects: "
        f"{ungrounded[:10]}"
    )
