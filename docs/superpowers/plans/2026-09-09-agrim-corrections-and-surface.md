# AGRIM corrections, new findings and surface rebuild — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct three defects in published numbers, add two findings modules nobody else has built, and restructure the dashboard surface to the corrected reference mockup without breaking the offline demo.

**Architecture:** No architectural change. D11 holds - no server, no API. New findings modules run at build time inside `findings/run.py` and write additive nullable fields into `web/public/data/*.json`. The frontend is restructured **in this repo**, in the existing Vite app: all ten screens already exist from tasks 16-18, so this is targeted rework of three of them plus shared components, not a rebuild. `web/dist` must keep serving from `python -m http.server` with Wi-Fi off.

**Tech Stack:** Python 3.12, pandas, scikit-learn (already wired, not touched here). Vite 8 + React + TypeScript + Tailwind v4, TanStack Table v8, ECharts 6, react-router-dom v6 hash routing, Ajv contract validation, `@fontsource` IBM Plex.

**Source spec:** `docs/superpowers/specs/2026-09-08-agrim-surface-and-phase-2-design.md`. Task numbers match the spec. Execution order differs from numeric order and is given in §Order below.

## Global Constraints

- **AGENTS.md rule 1.** Edit only the files a task lists, plus its tests.
- **AGENTS.md rule 2.** `contracts/` is read-only unless the task names the contract file. `findings.schema.json` has `additionalProperties: false` on `meta.headline` and on `field_audit`, so every new field **requires** a schema edit in the same task.
- **AGENTS.md rule 3.** Empty CSV cell = NULL = "not printed". Never write 0 or "NA". JSON uses `null`.
- **AGENTS.md rule 4.** Never hardcode a number that comes from the data. The web app and the deck read numbers from JSON.
- **AGENTS.md rule 5.** Determinism: `random_state=0`, `OMP_NUM_THREADS=1` in `findings/run.py`, JSON written with `sort_keys=True` and floats rounded to 4 decimals. Only `meta.generated_at` is a timestamp.
- **AGENTS.md rule 7.** No network at runtime.
- **AGENTS.md rule 8.** Before saying "done": run `python tools/validate.py` and `pytest -q` and **paste the output**.
- **AGENTS.md rule 9.** New dependency → `requirements.txt` AND re-freeze `requirements.lock` in the same commit. **No task in this plan adds a Python dependency.**
- **AGENTS.md rule 10.** Ambiguous spec line → implement the literal reading, leave a `# SPEC?` comment.
- **AGENTS.md rule 11.** Tick this plan's checkboxes as steps complete, commit them with the code.
- **AGENTS.md rule 12.** Commit messages: `task NN: <what>`.
- **D29.** Contract changes are additive and nullable only, with a minor version bump recorded in `contracts/CHANGELOG.md`.
- **D42.** Rule-based and model-based numbers are never blended.
- **Wording (Ranvir, 9 Sept).** The word is **"contradictions"**, never "impossibilities", on every screen, in `deck/numbers.json`, in the deck and in the pitch.
- **Models are frozen.** `findings/models/` and `models.json` metrics are not touched, retrained or re-tuned by any task here.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `findings/collapse.py` | **Create.** One pure function that merges consecutive same-type flags for display. Display-only; never applied before model feature building. | 21 |
| `findings/field_audit.py` | **Modify.** Add Whipple's index and its UN band to the existing terminal-digit output. | 21 |
| `findings/run.py` | **Modify.** Apply collapse after model scoring; emit `contradictions_arithmetic`, `statistical_anomalies`, `denominators`; wire `delay_series` and `escalation`. | 21, 23, 25 |
| `findings/delay_series.py` | **Create.** Reconstruct the discontinued delay bands per snapshot. | 23 |
| `findings/escalation.py` | **Create.** Sector-level delay rate, direction of travel, escalation flag. | 25 |
| `contracts/findings.schema.json` | **Modify.** Additive nullable fields for all of the above. | 21, 23, 25 |
| `contracts/CHANGELOG.md` | **Modify.** One minor bump entry per task. | 21, 23, 25 |
| `tools/routes.py` | **Create.** Serve `web/dist` and print every route URL for screenshot review. No new dependency. | 24 |
| `docs/SCREEN-CHECKLIST.md` | **Create.** The six pass conditions a screen must meet before its task is done. | 24 |
| `docs/FRONTEND-BRIEF.md` | **Create.** Internal reference: the data contract, the route table, the tokens, the demo path. Read it before touching a screen. | 22 |
| `docs/mockups/agrim-reference.html` | **Create.** Corrected, offline, honest reference mockup — Overview, Project evidence, Exit Ledger. The visual target every screen task is checked against. | 22 |
| `web/src/lib/format.ts` | **Modify.** Add `croreShort` for the abbreviated tile value. | 22 |
| `web/src/components/KPI.tsx` | **Modify.** Accept a `sub` line: abbreviated figure large, exact figure beneath. Drops the font-size clamp workaround. | 22 |
| `web/src/components/Caveat.tsx` | **Create.** The fixed “a contradiction is not an allegation” line, so the wording cannot drift. | 22 |
| `web/src/components/CsvButton.tsx` | **Create.** Download-this-table-as-CSV. No new dependency. | 22 |
| `web/src/screens/Overview.tsx` | **Modify.** Verdict sentence, corrected tiles, contradiction bars with anomalies split out, sector table labelled a rollup, sort by model probability. | 22 |
| `web/src/components/ShapBars.tsx` | **Create.** Diverging SHAP bars about a zero line, replacing the magic-pixel-width divs. | 26 |
| `web/src/components/Sparkline.tsx` | **Modify.** Severity-neutral ink; never the `ok` token for a trend line. | 26 |
| `web/src/components/SourcePage.tsx` | **Modify.** Add an inline variant rendering the page image at readable size, not behind a chip. | 26 |
| `web/src/screens/Project.tsx` | **Modify.** Promote the worst flag into a full-width evidence block with both source pages side by side. | 26 |
| `web/src/screens/Exits.tsx` | **Modify.** Caveat paragraph, neutral partition chips, pair bars scaled to the real maximum. | 27 |
| `web/src/screens/Warning.tsx` | **Modify.** Surface the reconstructed delay series from Task 23. | 27 |
| `web/src/screens/Drivers.tsx` | **Modify.** Surface the escalation matrix from Task 25. | 27 |
| `web/src/screens/Fields.tsx` | **Modify.** Call out Whipple's index and its band as a named statistic. | 27 |

---

## Mockup corrections

Three HTML mockups were produced by an external tool (Overview, Evidence Inspection, Exit Ledger). Their layout ideas are good and are kept. Their defects fall into six classes, all fixed in `docs/mockups/agrim-reference.html`, which is now the design target.

### Kept, because they are better than the current build

- **The two-panel evidence cockpit** on the project screen — source document left, structured reconciliation right. Stronger than the spec's original single evidence block; adopted.
- **The abbreviated-plus-full currency tile** — `₹ 37.10 L cr` large with `₹ 37,10,641.55 cr` beneath. This solves the three-line wrapping defect from §2.4 elegantly. Adopted.
- **Splitting arithmetic contradictions from statistical anomalies** into two separate tiles with distinct labels. This is exactly what Task 21 does in the data. Adopted.
- **The Exit Ledger's explanatory paragraph** stating that rows are classified only by last observed progress and never presumed cancelled. Good audit writing; kept nearly verbatim.
- **The panel-presence chronology timeline** on the project screen. Adopted, bound to `projects[].snapshots[]`.
- **Overall density, mono numerics, small radii, institutional chrome.** The direction is right.

### Class 1 — Breaks the offline demo (blocking)

| Defect | Fix |
|---|---|
| `<script src="https://cdn.tailwindcss.com">` | Tailwind v4 via `@tailwindcss/vite`, compiled at build time |
| Three `fonts.googleapis.com` stylesheet links | `@fontsource/ibm-plex-sans` + `@fontsource/ibm-plex-mono`, bundled |
| Material Symbols icon font from Google | Inline SVG sprite, or Phosphor (primary) / Heroicons (fallback) via npm — both tree-shaken and offline |
| JetBrains Mono substituted for IBM Plex Mono | Revert to IBM Plex Mono. D22 already decided it, the woff2 files are already committed in `web/dist/assets`, and switching costs a dependency for no gain |

The corrected reference makes **one** network request — itself. Verified with the browser network panel.

### Class 2 — Fabricated institutional authority (credibility-fatal)

The mockups invent a government system AGRIM is not: *"Auditor General / Senior Analyst #771"*, *"Gov Node #AGR-88021"*, *"TLS 1.3 / Air-Gapped Sync"*, *"Session Key #0x9F41C90B"*, *"National Node DEL-CP-08"*, *"v4.8-PROD"*, *"Air-Gap Batch #8819"*, *"OCR SHA256: 8f9a2..c3"*, *"AUDIT BOUNDING BOX #COORD-X412-Y778 [CONFIDENCE 99.8%]"*, *"SHA-VERIFIED"*, *"Rule #A-409"*, *"IPMD Taxonomy v3.4"*, *"RECORD ARCHIVE CLASS B-1"*, *"SECRECY CLASS: OFFICIAL USE ONLY"*, *"PRINTED BY GOVT PRESS"*.

**All removed.** AGRIM is a hackathon prototype reading five public PDFs. Claiming air-gapped government infrastructure, OCR confidence scores and secrecy classifications to a panel that may include MoSPI officials destroys the honesty the entire pitch rests on. The header now reads `AGRIM / IPMD / prototype`.

Two specific instances deserve naming:

- **The fake PDF page.** The mockup renders an *HTML emulation* of a government letterhead with an invented table. AGRIM has the real rendered page images at `/pages/<snapshot>/p<page>.png`. Showing a reconstruction instead of the real page throws away the single strongest asset in the project. The corrected version shows two real page images side by side — December 2025 page 74 and April 2026 page 88.
- **The "Agency Portal" column.** The reconciliation table compares *"Source PDF"* against *"Agency Portal"* and computes a variance. **AGRIM has no agency portal data** — the CUF is behind a login, which BUILD.md states as a known limitation and the model card declares. That column is a fabricated capability. The corrected version keeps the two-column reconciliation idea but the second column is **the previous month's published report**, which is what F1 actually compares and is honest.

### Class 3 — Token and colour-discipline violations

| Defect | Fix |
|---|---|
| `primary: #000000`, `secondary: #0051d5`, `error: #ba1a1a` | The BUILD.md §8 tokens exactly: ink `#0E1A2B`, accent `#1F5FA8`, critical `#B42318` |
| **`#5B4B9A` absent entirely.** Model output rendered in `secondary` blue (same as links) and an unrelated `tertiary` purple | Every model-derived value in `--model: #5B4B9A`, with the word "model" beside it. Used 12 times in the corrected reference |
| `bg-[#16a34a]`, `bg-[#dcfce7]`, `bg-amber-500`, `bg-blue-500`, `from-blue-300 via-amber-400 to-red-700` | Removed. Severity tokens only |
| Exit partition `≥95% when last seen` coloured green as "good" | Neutral. A project last seen at 98% that vanished is arguably the *most* suspicious row on the screen — colouring it as success is colour used decoratively and inverts the finding |
| `borderRadius.full: 0.75rem` overrides `rounded-full`, so every status dot renders as a rounded square | Radii 2–3px on containers, true circles for dots |
| Severity conveyed by colour alone in several chips | Severity encoded twice — colour **and** word — per BUILD.md §8 and the `ux` domain's `Color Only` rule (severity: High) |

### Class 4 — Fabricated data and hardcoded numbers

Invented and presented as real: `Total Flagged: 1,489`, `17 Sectors` (actual: 22), the entire sector table (`Roads & Highways 786/993` etc.), every per-state map figure, every exit-pair count (`50/690/10`), `₹ 8,87,388.66 cr`, `190` early-warning badge (actual unreachable: 1,289), the six exit roster rows, `IF-v2.1`, anomaly score `0.942`, `+16 mos drift`.

This violates AGENTS.md rule 4 directly. In the corrected reference **every number carries `data-bind="<json path>"`**; values verified in this session are shown, and anything unverified renders as an em dash with its bind path attached — never as a plausible-looking invention. The mockup doubles as binding documentation for the port.

One thing the mockups got *right*: the header chip `5 reports · 8837 rows · 98.3% parsed` is accurate. Mean of the five coverage percentages is 98.338.

### Class 5 — React, SVG and correctness bugs

| Defect | Fix |
|---|---|
| Lowercased SVG attributes: `viewbox`, `preserveaspectratio`, `lineargradient`, `radialgradient`, `fegaussianblur`, `fecomposite`, `stop-color` | JSX requires camelCase: `viewBox`, `preserveAspectRatio`, `linearGradient`, `radialGradient`, `feGaussianBlur`, `feComposite`, `stopColor`. These fail silently or throw in React |
| Four duplicated DOM ids (`zoom-out-btn`, `zoom-readout`, `zoom-in-btn`, `fullscreen-doc-btn` in both toolbars) | Unique ids. Verified: zero duplicates in the corrected reference |
| `class="px- space-sm"` — typo with an embedded space | Fixed |
| Inline `<script>` rewriting `aside nav a` classNames to set the active tab | `NavLink` with `isActive`. Imperative DOM edits fight React's reconciler |
| Hand-drawn India polygons with approximated boundaries | DataMeet GeoJSON via ECharts `registerMap`, post-2019 J&K/Ladakh verified (D18). An approximated India outline in a government room is a serious problem |
| `::-webkit-scrollbar{display:none}` globally | Removed. Hiding scrollbars removes the only cue that content scrolls |
| Static `<div>` with a caret acting as the persona switch | A real `<select>` with a label |
| Icon-only buttons with no accessible name | `aria-label` or visible text on every control |

### Class 6 — Motion

`laserScan` (4.5s infinite scanning laser over the document), `pulseRadar`, `shimmerSweep`, `pathStrokeDraw`, and roughly a dozen `animate-ping` / `animate-pulse` instances. BUILD.md §8 permits nothing beyond a 150–200 ms fade, and the `ux` domain flags decorative-only animation. All removed; the corrected reference has one transition, a 150 ms button hover, plus a `prefers-reduced-motion` block.

A scanning laser over an evidence document reads as theatre. The evidence is the argument; it does not need a special effect.

**Why `collapse.py` is its own file:** `contradictions.detect()` must stay pure so the existing fixture tests keep asserting raw detection counts, and because `findings/models/features.py` consumes the **raw** flag list to build `n_flags_to_t0` and `exp_decrease_ever` for feature set B. Collapsing before model scoring would change M1's features and silently invalidate the frozen PR-AUC numbers already on the Predictions screen and in `deck/numbers.json`.

---

## Order

Execution order, not numeric order. Today is Wed 9 Sept; the round is Sat 12 Sept.

**Status as of 9 Sept, verified.** Tasks 1-20 are all complete and merged to `main` (PR #2, commit `3802930`). The relay plan shows 124 of 126 checkboxes ticked; the two open items are human tasks - fill the official PPTX template by hand, and rehearse on a cold machine. Tasks 18, 19 and 20 landed on the evening of 8 Sept, so **the deck already exists** and `tools/slides.py` renders `deck/slides.md` from `deck/numbers.json` automatically.

That last fact removes the original reason for a hard numbers freeze: the deck is generated, not hand-written, so a numbers change re-renders rather than invalidating hours of work. The freeze still applies to the PPTX that gets filled in by hand.

| When | Tasks | Gate |
|---|---|---|
| Wed 9 | 21 -> 23 -> 25 | Full run, `validate.py` + `pytest -q` pasted, `deck/numbers.json` regenerated, `python tools/slides.py` re-run |
| Wed 9 evening | 24 | Checklist and route enumerator working |
| Thu 10 | 22 -> 26 -> 27 | Every touched route screenshot-checked against the six conditions; the four guard greps return nothing |
| Thu 10 evening | Re-run `tools/slides.py`, fill the official PPTX by hand, export to PDF once | Relay plan Task 20 Step 3 |
| Fri 11 | Cold-machine rehearsal twice, Wi-Fi off, fresh clone, `RUN_DEMO.bat`. Three timed pitch runs. | Relay plan Task 20 Step 5. Bug fixes only |

**Cut line.** Wednesday 22:00: if Task 23 or 25 is not producing a number you would defend to a MoSPI officer, drop it and make it a "next step" line on the slide. Thursday 22:00: the CSV-export affordance in Task 22 Step 4. **Never cut:** Task 21, Task 26 (the Project evidence block), the PPTX, the rehearsal. Task 27 sheds work cleanly - its four steps are independent screens, so drop steps rather than the task.

**The screen tasks carry the only real risk.** Tasks 16-18 already shipped a working, committed `web/dist` that runs offline. Tasks 22, 26 and 27 edit that working surface, so each ends with a build, a screenshot check and the four guard greps before it is called done. `git checkout main -- web/dist` restores a working build if one goes wrong.

---

### Task 21: Findings corrections

**Files:**
- Create: `findings/collapse.py`
- Create: `tests/findings/test_collapse.py`
- Modify: `findings/field_audit.py`
- Modify: `findings/run.py`
- Modify: `contracts/findings.schema.json`
- Modify: `contracts/CHANGELOG.md`
- Modify: `tests/findings/test_contradictions.py` (two existing assertions change; see Step 6)
- Modify: `tools/slides.py` (the deck template quotes the wrong number; see Step 11b)
- Test: `tests/findings/test_field_audit_whipple.py`

**Interfaces:**
- Produces: `findings.collapse.collapse(flags: list[dict]) -> list[dict]`. Input and output flags carry the same keys plus `first_snapshot: str | None` and `occurrences: int` on every returned flag. Sort order of the output is `(project_code, to_snapshot, type)`, identical to `contradictions.detect`.
- Produces: `findings.field_audit.whipple_index(digit_counts: dict[int, int]) -> float | None` and `findings.field_audit.whipple_band(w: float | None) -> str | None`.
- Produces: `findings.meta.headline.contradictions_arithmetic: int`, `findings.meta.headline.statistical_anomalies: int`, `findings.meta.denominators: object`.
- Consumes: nothing from other tasks in this plan.

- [x] **Step 1: Write the failing test for flag collapse**

Create `tests/findings/test_collapse.py`:

```python
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
```

- [x] **Step 2: Run it to make sure it fails**

Run: `pytest tests/findings/test_collapse.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'findings.collapse'`

- [x] **Step 3: Implement the minimal code to make the test pass**

Create `findings/collapse.py`:

```python
"""Display-only: merge consecutive same-type flags on the same project into one row.

Never apply this before findings.models.features builds feature set B — that reads the
raw flag list for n_flags_to_t0 and exp_decrease_ever, and collapsing first would change
M1's features and invalidate the frozen metrics.
"""


def collapse(flags):
    groups = {}
    order = []
    for f in flags:
        key = (f["project_code"], f["type"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(f)
    out = []
    for key in order:
        members = sorted(groups[key], key=lambda f: f["to_snapshot"])
        head = dict(members[-1])
        head["first_snapshot"] = members[0]["from_snapshot"] or members[0]["to_snapshot"]
        head["occurrences"] = len(members)
        seen, sources = set(), []
        for m in members:
            for s in m["sources"]:
                k = (s["snapshot"], s["page"])
                if k not in seen:
                    seen.add(k)
                    sources.append(s)
        head["sources"] = sorted(sources, key=lambda s: (s["snapshot"], s["page"]))
        out.append(head)
    out.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return out
```

- [x] **Step 4: Run the tests and make sure they pass**

Run: `pytest tests/findings/test_collapse.py -q`
Expected: PASS, 6 passed

- [x] **Step 5: Write the failing test for Whipple's index**

Create `tests/findings/test_field_audit_whipple.py`:

```python
from findings.field_audit import whipple_band, whipple_index


def test_uniform_terminal_digits_score_one_hundred():
    assert whipple_index({d: 100 for d in range(10)}) == 100.0


def test_every_value_on_zero_or_five_scores_five_hundred():
    assert whipple_index({0: 500, 5: 500}) == 500.0


def test_no_observations_returns_none():
    assert whipple_index({}) is None
    assert whipple_index({d: 0 for d in range(10)}) is None


def test_bands_follow_the_un_thresholds():
    assert whipple_band(102.0) == "very accurate"
    assert whipple_band(107.0) == "relatively accurate"
    assert whipple_band(120.0) == "approximate"
    assert whipple_band(150.0) == "rough"
    assert whipple_band(200.0) == "very rough"
    assert whipple_band(None) is None
```

- [x] **Step 6: Run it to make sure it fails**

Run: `pytest tests/findings/test_field_audit_whipple.py -q`
Expected: FAIL — `ImportError: cannot import name 'whipple_index'`

- [x] **Step 7: Implement Whipple's index**

In `findings/field_audit.py`, add above `compute`:

```python
BANDS = [(105, "very accurate"), (110, "relatively accurate"), (125, "approximate"), (175, "rough")]


def whipple_index(digit_counts):
    """Digit-heaping index over terminal digits. 100 = no preference, 500 = every value on 0 or 5.

    Whipple, not Benford: physical progress is bounded 0-100, so Benford's Law does not apply.
    """
    n = sum(digit_counts.values())
    if not n:
        return None
    return round(100.0 * (digit_counts.get(0, 0) + digit_counts.get(5, 0)) / (0.2 * n), 4)


def whipple_band(w):
    if w is None:
        return None
    for limit, name in BANDS:
        if w < limit:
            return name
    return "very rough"
```

Then in `compute`, add both to the returned dict, after `"multiple_of_10_share"`:

```python
            "whipple_index": whipple_index(digits),
            "whipple_band": whipple_band(whipple_index(digits)),
```

- [x] **Step 8: Run the tests and make sure they pass**

Run: `pytest tests/findings/test_field_audit_whipple.py -q`
Expected: PASS, 4 passed

- [x] **Step 9: Update the two existing assertions that the collapse changes**

`tests/findings/test_contradictions.py` asserts raw detection counts and **must keep doing so** — `detect()` is unchanged, so that file needs no edit. Confirm this by running it:

Run: `pytest tests/findings/test_contradictions.py -q`
Expected: PASS, unchanged. If it fails, you have wrongly modified `detect()` — revert that and put the logic in `collapse.py`.

- [x] **Step 10: Extend the contract, additively**

In `contracts/findings.schema.json`:

1. In `properties.meta.properties.headline.properties`, add `"contradictions_arithmetic": {"type": "integer"}` and `"statistical_anomalies": {"type": "integer"}`. Add both names to that object's `required` array.
2. In `properties.meta.properties`, add:

```json
"denominators": {
 "type": "object",
 "additionalProperties": false,
 "required": ["cost_revised_null", "cost_overrun_null", "doc_null"],
 "properties": {
  "cost_revised_null": {"type": "integer"},
  "cost_overrun_null": {"type": "integer"},
  "doc_null": {"type": "integer"}
 }
}
```

and add `"denominators"` to `properties.meta.required`.

3. In `properties.field_audit.properties`, add `"whipple_index": {"type": ["number", "null"]}` and `"whipple_band": {"type": ["string", "null"]}`, and add both to `properties.field_audit.required`.

In `contracts/CHANGELOG.md`, add one entry: minor bump to `1.1.0`, listing the five new fields and naming task 21.

Set `CONTRACT_VERSION = "1.1.0"` in `findings/run.py`.

- [x] **Step 11: Wire collapse, the split headline and the denominators into run.py**

In `findings/run.py`:

Add the import beside the others: `from findings import assistant, collapse as collapse_mod, contradictions, ...`

In `build()`, apply collapse **after** `run_models` has consumed the raw flags:

```python
    projects = build_projects(panel, flags, ex["status"], sectors, ml_by_code)
```

becomes

```python
    display_flags = collapse_mod.collapse(flags)  # display only; models already scored on raw flags
    projects = build_projects(panel, display_flags, ex["status"], sectors, ml_by_code)
    findings = build_findings(panel, projects, display_flags, ex, ew, aggregates, models)
```

and delete the old `findings = build_findings(panel, projects, flags, ...)` line so `build_findings` is called exactly once.

In `build_findings`, replace the `headline` dict with:

```python
                 "headline": {"projects_latest": len(latest_rows), "cost_revised_total_cr": round(cost_rev, 2), "overrun_total_cr": round(overrun, 2),
                              "contradictions_total": len(c_rows),
                              "contradictions_arithmetic": sum(1 for f in c_rows if f["type"] in ARITH),
                              "statistical_anomalies": sum(1 for f in c_rows if f["type"] == "STAT_ANOMALY"),
                              "exits_total": sum(p["exited"] for p in ex["pairs"]),
                              "unreachable_total": sum(1 for f in flags if f["type"] == "DOC_UNREACHABLE"), "watchlist_size": len(watch)},
                 "denominators": {
                     "cost_revised_null": sum(1 for r in latest_rows if r["cost_revised_cr"] is None),
                     "cost_overrun_null": sum(1 for r in latest_rows if r["cost_revised_cr"] is None or r["cost_original_cr"] is None),
                     "doc_null": sum(1 for r in latest_rows if r["doc_revised"] is None and r["doc_original"] is None)},
```

In `deck_numbers`, add after the existing `contradictions_total` entry:

```python
            "contradictions_arithmetic": h["contradictions_arithmetic"], "statistical_anomalies": h["statistical_anomalies"],
```

- [x] **Step 11b: Fix the deck slide, which currently contradicts itself**

`tools/slides.py` renders `deck/slides.md` from `deck/numbers.json`. Its slide 2 template reads:

> we found `{contradictions_total}` arithmetic impossibilities in the Ministry's own published numbers

and later on the same slide:

> `{count_STAT_ANOMALY}` statistical outliers from an isolation forest - model output, shown beside the rule-based ledger and never counted into its total

`contradictions_total` is 1,101 and **does** include the 134 anomalies, so the slide asserts something the number disproves. This is on a judge-facing slide.

Two changes to the `TEMPLATE` string:

1. Replace `{contradictions_total}` with `{contradictions_arithmetic}` in the slide-2 line.
2. Replace the words "arithmetic impossibilities" with "contradictions", per the wording decision in Global Constraints. Search the whole file - the phrase may appear more than once.

Then re-render and confirm the slide is self-consistent:

```bash
python tools/slides.py
pytest tests/tools/test_slides.py -q
grep -n "impossibilit" deck/slides.md tools/slides.py deck/pitch.md
```
Expected: `slides.py` writes the file, the test passes, and the grep returns **no output**. If `test_slides.py` reports a leftover `{...}` placeholder, the key is missing from `deck/numbers.json` - add it in `deck_numbers()` in Step 11, never by typing the number into the slide.

- [x] **Step 12: Run the full pipeline and both gates**

Run:
```bash
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json
python tools/validate.py
pytest -q
```
Expected: the run prints a project count and a contradictions count; `validate.py` exits 0; all tests pass. **Paste all three outputs into the relay log.** Confirm `deck/numbers.json` now contains `contradictions_arithmetic: 967` and `statistical_anomalies: 134`. If `contradictions_arithmetic` is not 967, stop and report — do not adjust the number to match.

- [x] **Step 13: Commit**

```bash
git add findings/collapse.py findings/field_audit.py findings/run.py tools/slides.py contracts/findings.schema.json contracts/CHANGELOG.md tests/findings/test_collapse.py tests/findings/test_field_audit_whipple.py web/public/data deck/numbers.json deck/slides.md docs/superpowers/plans/2026-09-09-agrim-corrections-and-surface.md
git commit -m "task 21: split the contradictions headline, collapse repeat flags, denominators, Whipple index"
```

---

### Task 23: Delay-series reconstruction

**Files:**
- Create: `findings/delay_series.py`
- Create: `tests/findings/test_delay_series.py`
- Modify: `findings/run.py`
- Modify: `contracts/findings.schema.json`
- Modify: `contracts/CHANGELOG.md`

**Interfaces:**
- Consumes: `findings.panel.load_panel`, `findings.panel.series`, `findings.panel.months`, `findings.panel.snapshots_present` (all already exist).
- Produces: `findings.delay_series.compute(panel) -> dict` shaped `{"bands": [str, ...], "rows": [{"snapshot": str, "on_schedule": int, "d_1_12": int, "d_13_24": int, "d_25_60": int, "d_61_plus": int, "classifiable": int, "doc_null": int}, ...]}`.
- Produces: `findings.delay_series` under key `delay_series` in `findings.json`.

**Definition, from the April 2014 Flash Report's own bands.** For each snapshot, for each project present in that snapshot:

- If `doc_original` is NULL → not classifiable, counted in `doc_null`.
- Else if `doc_revised` is present → `delay = months(doc_original, doc_revised)`.
- Else → `delay = months(doc_original, snapshot)` when the snapshot month is later than `doc_original`, otherwise `0`.
- Bands: `delay <= 0` on schedule; `1-12`; `13-24`; `25-60`; `61+`.

This is the literal reading of "delayed against the stated original schedule". Leave a `# SPEC?` comment on the unrevised-but-overdue branch, per AGENTS.md rule 10.

- [x] **Step 1: Write the failing test**

Create `tests/findings/test_delay_series.py`:

```python
import pandas as pd

from findings.delay_series import classify, compute
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def test_no_original_date_is_not_classifiable():
    assert classify(None, None, "2026-07") is None
    assert classify(None, "2027-01", "2026-07") is None


def test_revised_date_measures_against_the_original():
    assert classify("2026-01", "2026-07", "2026-07") == 6
    assert classify("2026-01", "2031-01", "2026-07") == 60


def test_unrevised_but_overdue_measures_against_the_snapshot():
    assert classify("2026-01", None, "2026-07") == 6


def test_unrevised_and_not_yet_due_is_on_schedule():
    assert classify("2027-01", None, "2026-07") == 0


def test_a_revised_date_earlier_than_the_original_is_on_schedule():
    assert classify("2026-07", "2026-01", "2026-07") == -6


def test_bands_partition_every_classifiable_project():
    out = compute(load_panel(FIX))
    for row in out["rows"]:
        total = row["on_schedule"] + row["d_1_12"] + row["d_13_24"] + row["d_25_60"] + row["d_61_plus"]
        assert total == row["classifiable"]


def test_every_snapshot_in_the_panel_gets_a_row():
    panel = load_panel(FIX)
    out = compute(panel)
    assert [r["snapshot"] for r in out["rows"]] == sorted(set(panel["snapshot"]), key=lambda s: (s[:4], s[5:]))


def test_null_doc_is_counted_not_dropped():
    out = compute(load_panel(FIX))
    for row in out["rows"]:
        assert row["doc_null"] >= 0
        assert isinstance(row["doc_null"], int)
```

- [x] **Step 2: Run it to make sure it fails**

Run: `pytest tests/findings/test_delay_series.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'findings.delay_series'`

- [x] **Step 3: Implement the minimal code to make the test pass**

Create `findings/delay_series.py`:

```python
"""Reconstruct the delay classification the Flash Reports stopped printing.

The April 2014 report bucketed projects behind schedule into up to 12 months, 13-24,
25-60, and 61 months and above. The April 2026 report does not use the word at all.
The fields it still prints are enough to recompute the same bands. This is a
continuity-of-series reconstruction, not an accusation.
"""
from findings.panel import months, series, snapshots_present

BANDS = ["on_schedule", "d_1_12", "d_13_24", "d_25_60", "d_61_plus"]


def classify(doc_original, doc_revised, snapshot):
    """Months late against the original stated completion date. None if not classifiable."""
    if not doc_original:
        return None
    if doc_revised:
        return months(doc_original, doc_revised)
    # SPEC? An unrevised project past its own stated date is treated as late by the
    # elapsed months. The literal reading of "delayed against the stated schedule".
    gap = months(doc_original, snapshot)
    return gap if gap > 0 else 0


def _band(delay):
    if delay <= 0:
        return "on_schedule"
    if delay <= 12:
        return "d_1_12"
    if delay <= 24:
        return "d_13_24"
    if delay <= 60:
        return "d_25_60"
    return "d_61_plus"


def compute(panel):
    rows = []
    by_snapshot = {s: {b: 0 for b in BANDS} | {"doc_null": 0} for s in snapshots_present(panel)}
    for _, rs in series(panel).items():
        for r in rs:
            bucket = by_snapshot[r["snapshot"]]
            delay = classify(r["doc_original"], r["doc_revised"], r["snapshot"])
            if delay is None:
                bucket["doc_null"] += 1
            else:
                bucket[_band(delay)] += 1
    for s in snapshots_present(panel):
        b = by_snapshot[s]
        rows.append({"snapshot": s, **{k: b[k] for k in BANDS},
                     "classifiable": sum(b[k] for k in BANDS), "doc_null": b["doc_null"]})
    return {"bands": BANDS, "rows": rows}
```

- [x] **Step 4: Run the tests and make sure they pass**

Run: `pytest tests/findings/test_delay_series.py -q`
Expected: PASS, 8 passed

- [x] **Step 5: Extend the contract**

In `contracts/findings.schema.json`, add to `properties`:

```json
"delay_series": {
 "type": "object",
 "additionalProperties": false,
 "required": ["bands", "rows"],
 "properties": {
  "bands": {"type": "array", "items": {"type": "string"}},
  "rows": {"type": "array", "items": {
    "type": "object", "additionalProperties": false,
    "required": ["snapshot", "on_schedule", "d_1_12", "d_13_24", "d_25_60", "d_61_plus", "classifiable", "doc_null"],
    "properties": {
     "snapshot": {"type": "string"}, "on_schedule": {"type": "integer"},
     "d_1_12": {"type": "integer"}, "d_13_24": {"type": "integer"},
     "d_25_60": {"type": "integer"}, "d_61_plus": {"type": "integer"},
     "classifiable": {"type": "integer"}, "doc_null": {"type": "integer"}}}}
 }
}
```

Add `"delay_series"` to the schema's top-level `required` array. Bump to `1.2.0` in `contracts/CHANGELOG.md` and in `findings/run.py`'s `CONTRACT_VERSION`.

- [x] **Step 6: Wire it into run.py**

Add `delay_series` to the `from findings import ...` line. In `build_findings`, add to the `findings` dict after `"field_audit"`:

```python
        "delay_series": delay_series.compute(panel),
```

In `deck_numbers`, add after the coverage loop:

```python
    last_delay = findings["delay_series"]["rows"][-1]
    for k in ["on_schedule", "d_1_12", "d_13_24", "d_25_60", "d_61_plus", "classifiable", "doc_null"]:
        nums[f"delay_{k}"] = last_delay[k]
```

- [x] **Step 7: Run the full pipeline and both gates**

Run:
```bash
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json
python tools/validate.py
pytest -q
```
Expected: all three succeed. **Paste the output.** Read the reconstructed bands out loud as a sentence — "of N classifiable projects in July 2026, X are more than 60 months past their original date, and M have no original date at all". If that sentence is not one you would say to a MoSPI officer, invoke the Wednesday 22:00 cut rather than shipping it.

- [x] **Step 8: Commit**

```bash
git add findings/delay_series.py tests/findings/test_delay_series.py findings/run.py contracts/findings.schema.json contracts/CHANGELOG.md web/public/data deck/numbers.json docs/superpowers/plans/2026-09-09-agrim-corrections-and-surface.md
git commit -m "task 23: reconstruct the discontinued delay bands across five snapshots"
```

---

### Task 25: Escalation matrix

**Files:**
- Create: `findings/escalation.py`
- Create: `tests/findings/test_escalation.py`
- Modify: `findings/run.py`
- Modify: `contracts/findings.schema.json`
- Modify: `contracts/CHANGELOG.md`

**Interfaces:**
- Consumes: `findings.delay_series.classify` (Task 23), `findings.panel.series`, `findings.panel.snapshots_present`, `findings.panel.sector_map`.
- Produces: `findings.escalation.compute(panel, sectors) -> dict` shaped `{"threshold_pct": 50.0, "rows": [{"key": str, "projects": int, "classifiable": int, "delayed": int, "delay_rate_pct": float | None, "first_rate_pct": float | None, "improving": bool | None, "escalate": bool}, ...]}`, sorted by `delay_rate_pct` descending then `key` ascending.
- Produces: key `escalation` in `findings.json`.

**Rule, from the Standing Committee recommendation.** Flag a rollup for escalation where its delay rate in the latest snapshot exceeds 50% **and** that rate is not lower than its rate in the first snapshot where it had classifiable projects. `improving` is `True` when the latest rate is below the first rate, `False` when it is not, and `null` when there is only one snapshot of data. **Cite no report number or date anywhere** — the attribution between BUILD.md §2 and the research is unresolved; the finding stands on the counts.

**Rollup caveat.** `sector` comes from D15's agency-string rollup. Any screen showing this must say it is a rollup, not a mapping to the 17 official ministries.

- [x] **Step 1: Write the failing test**

Create `tests/findings/test_escalation.py`:

```python
from findings.escalation import compute
from findings.panel import load_panel, sector_map

FIX = "contracts/fixtures/panel.sample.csv"


def test_rows_are_sorted_by_delay_rate_descending():
    panel = load_panel(FIX)
    out = compute(panel, sector_map(panel))
    rates = [(-(r["delay_rate_pct"] if r["delay_rate_pct"] is not None else -1), r["key"]) for r in out["rows"]]
    assert rates == sorted(rates)


def test_threshold_is_fifty_percent():
    panel = load_panel(FIX)
    assert compute(panel, sector_map(panel))["threshold_pct"] == 50.0


def test_escalate_requires_both_a_high_rate_and_no_improvement():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        if r["escalate"]:
            assert r["delay_rate_pct"] > 50.0
            assert r["improving"] is not True


def test_a_rollup_with_no_classifiable_projects_has_a_null_rate_and_is_not_escalated():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        if r["classifiable"] == 0:
            assert r["delay_rate_pct"] is None and r["escalate"] is False


def test_delayed_never_exceeds_classifiable():
    panel = load_panel(FIX)
    for r in compute(panel, sector_map(panel))["rows"]:
        assert 0 <= r["delayed"] <= r["classifiable"] <= r["projects"]
```

- [x] **Step 2: Run it to make sure it fails**

Run: `pytest tests/findings/test_escalation.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'findings.escalation'`

- [x] **Step 3: Implement the minimal code to make the test pass**

Create `findings/escalation.py`:

```python
"""Per-rollup delay rate, direction of travel, and an escalation flag.

Implements the structured escalation matrix a parliamentary committee recommended:
flag rollups whose delay rate exceeds 50% and is not improving. No report number or
date is cited here; the attribution is unresolved and the finding stands on the counts.

The rollup key is the agency-derived sector of D15. It is a rollup, not a mapping to
the 17 official ministries, and any screen showing it must say so.
"""
from findings.delay_series import classify
from findings.panel import series, snapshots_present

THRESHOLD_PCT = 50.0


def _rate(delayed, classifiable):
    return round(100.0 * delayed / classifiable, 4) if classifiable else None


def compute(panel, sectors):
    snaps = snapshots_present(panel)
    first, last = snaps[0], snaps[-1]
    agg = {}
    for code, rs in series(panel).items():
        key = sectors.get(code) or "UNKNOWN"
        a = agg.setdefault(key, {"projects": set(), "first": [0, 0], "last": [0, 0]})
        a["projects"].add(code)
        for r in rs:
            if r["snapshot"] not in (first, last):
                continue
            slot = a["first"] if r["snapshot"] == first else a["last"]
            delay = classify(r["doc_original"], r["doc_revised"], r["snapshot"])
            if delay is None:
                continue
            slot[1] += 1
            if delay > 0:
                slot[0] += 1
    rows = []
    for key, a in agg.items():
        d_last, c_last = a["last"]
        d_first, c_first = a["first"]
        rate, first_rate = _rate(d_last, c_last), _rate(d_first, c_first)
        improving = None if first_rate is None or rate is None else rate < first_rate
        rows.append({"key": key, "projects": len(a["projects"]), "classifiable": c_last, "delayed": d_last,
                     "delay_rate_pct": rate, "first_rate_pct": first_rate, "improving": improving,
                     "escalate": bool(rate is not None and rate > THRESHOLD_PCT and improving is not True)})
    rows.sort(key=lambda r: (-(r["delay_rate_pct"] if r["delay_rate_pct"] is not None else -1), r["key"]))
    return {"threshold_pct": THRESHOLD_PCT, "rows": rows}
```

- [x] **Step 4: Run the tests and make sure they pass**

Run: `pytest tests/findings/test_escalation.py -q`
Expected: PASS, 5 passed

- [x] **Step 5: Extend the contract**

In `contracts/findings.schema.json`, add to `properties`:

```json
"escalation": {
 "type": "object",
 "additionalProperties": false,
 "required": ["threshold_pct", "rows"],
 "properties": {
  "threshold_pct": {"type": "number"},
  "rows": {"type": "array", "items": {
    "type": "object", "additionalProperties": false,
    "required": ["key", "projects", "classifiable", "delayed", "delay_rate_pct", "first_rate_pct", "improving", "escalate"],
    "properties": {
     "key": {"type": "string"}, "projects": {"type": "integer"},
     "classifiable": {"type": "integer"}, "delayed": {"type": "integer"},
     "delay_rate_pct": {"type": ["number", "null"]}, "first_rate_pct": {"type": ["number", "null"]},
     "improving": {"type": ["boolean", "null"]}, "escalate": {"type": "boolean"}}}}
 }
}
```

Add `"escalation"` to the top-level `required` array. Bump to `1.3.0` in `contracts/CHANGELOG.md` and in `findings/run.py`'s `CONTRACT_VERSION`.

- [x] **Step 6: Wire it into run.py**

Add `escalation` to the `from findings import ...` line. In `build_findings`, add after `"delay_series"`:

```python
        "escalation": escalation.compute(panel, sector_map(panel)),
```

In `deck_numbers`, add:

```python
    nums["escalation_flagged"] = sum(1 for r in findings["escalation"]["rows"] if r["escalate"])
```

- [x] **Step 7: Run the full pipeline and both gates**

Run:
```bash
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json
python tools/validate.py
pytest -q
```
Expected: all three succeed. **Paste the output.** Then run the pipeline a second time and confirm `git diff --stat web/public/data` is empty — this is the determinism check required by AGENTS.md rule 5.

- [x] **Step 8: Commit — this is the numbers freeze**

```bash
git add findings/escalation.py tests/findings/test_escalation.py findings/run.py contracts/findings.schema.json contracts/CHANGELOG.md web/public/data deck/numbers.json docs/superpowers/plans/2026-09-09-agrim-corrections-and-surface.md
git commit -m "task 25: escalation matrix over the reconstructed delay rate"
```

After this commit, `deck/numbers.json` is **frozen**. Task 20 writes the deck against it. Any later change to a published number requires re-running Task 20's slide checks.

---

### Task 24: The visual arbiter

**Files:**
- Create: `tools/routes.py`
- Create: `docs/SCREEN-CHECKLIST.md`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `python tools/routes.py` serves `web/dist` on port 8080 and prints one URL per route to stdout.
- Consumes: nothing.

**No new dependency.** This deliberately does not install a headless browser — Playwright would need a runtime download, which AGENTS.md rule 7 forbids, and a lock re-freeze the schedule cannot absorb. The script serves and enumerates; whoever runs the task takes the screenshots with the browser tool they already have.

- [x] **Step 1: Write the route enumerator**

Create `tools/routes.py`:

```python
"""Serve the built dashboard and print every route to screenshot. No new dependency.

    python tools/routes.py            # serve on 8080 and list routes
    python tools/routes.py --list     # list only, do not serve
"""
import argparse
import functools
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "web" / "dist"
ROUTES = ["/", "/ledger", "/exits", "/fields", "/warning", "/predict", "/drivers",
          "/assistant", "/model-card", "/project/705410"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if not DIST.exists():
        print(f"no build at {DIST}; run npm run build in web/ first", file=sys.stderr)
        return 1
    base = f"http://localhost:{a.port}"
    for r in ROUTES:
        print(f"{base}/#{r}")
    print(f"\nchecklist: {ROOT / 'docs' / 'SCREEN-CHECKLIST.md'}")
    if a.list:
        return 0
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with socketserver.TCPServer(("", a.port), handler) as httpd:
        print(f"\nserving {DIST} at {base} — ctrl-c to stop")
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Run it to verify it lists ten routes**

Run: `python tools/routes.py --list`
Expected: ten `http://localhost:8080/#/...` lines plus the checklist path, exit 0.

- [x] **Step 3: Write the checklist**

Create `docs/SCREEN-CHECKLIST.md`:

```markdown
# Screen checklist

Tasks 1-17 had `tools/validate.py` and `pytest -q` deciding whether output was correct.
The screens had no arbiter, and came out as six identical cards per page. This is the
arbiter. A screen task is not done until every route's screenshot has been checked
against all six conditions and the screenshots are attached to the task.

Run `python tools/routes.py`, open each URL at 1440x900, screenshot, then check:

1. **No number wraps.** No figure breaks across lines. `₹ 37,10,641.55 cr` fits one line.
2. **No dead column.** No table column shows the same value in every visible row.
3. **Colour means severity.** critical/high/medium/ok are used only for severity.
   No colour is decorative. A falling trend is never drawn in the `ok` green.
4. **Model numbers are marked.** Every model-derived figure is in `#5B4B9A` and the
   word "model" appears beside it.
5. **One focal point.** The screen has a single thing the eye lands on first. Not six
   equal cards.
6. **Provenance.** Every displayed figure either traces to a page citation or is
   explicitly labelled model-derived.

Wording: the headline word is **contradictions**, never "impossibilities".
```

- [x] **Step 4: Ignore the screenshot output directory**

Append to `.gitignore`:

```
web/shots/
```

- [x] **Step 5: Commit**

```bash
git add tools/routes.py docs/SCREEN-CHECKLIST.md .gitignore docs/superpowers/plans/2026-09-09-agrim-corrections-and-surface.md
git commit -m "task 24: route enumerator and the screen checklist"
```

---

### Task 22: Shared primitives and the Overview verdict

**Files:** `web/src/lib/format.ts`, `web/src/components/KPI.tsx`, `web/src/components/Caveat.tsx` (create), `web/src/components/CsvButton.tsx` (create), `web/src/screens/Overview.tsx`.

**Interfaces:**
- Consumes: `findings.meta.headline.contradictions_arithmetic`, `.statistical_anomalies`, and `findings.meta.denominators` from Task 21.
- Produces: `croreShort(v: number | null) => string`; `<KPI label value sub? hint? model? />`; `<Caveat />`; `<CsvButton rows filename />`.

Open `docs/mockups/agrim-reference.html` at `#/` first. It is the target.

- [x] **Step 1: Add the abbreviated crore formatter**

In `web/src/lib/format.ts`:

```ts
// A 12-digit crore figure does not fit a tile. Show it abbreviated, exact value beneath.
export const croreShort = (v: number | null | undefined) => {
  if (v == null) return "—";
  if (v >= 100000) return `₹ ${(v / 100000).toFixed(2)} L cr`;
  if (v >= 1000) return `₹ ${(v / 1000).toFixed(2)} K cr`;
  return crore(v);
};
```

- [x] **Step 2: Give KPI a sub line and drop the font clamp**

`KPI.tsx` currently shrinks the figure with `[font-size:clamp(1rem,1.4vw,1.5rem)]` so a long number fits. Replace that workaround: hold the display size and add an optional `sub` line beneath.

```tsx
export function KPI({ label, value, sub, hint, model = false }:
  { label: string; value: string; sub?: string; hint?: string; model?: boolean }) {
  return (
    <div className={`rounded border bg-surface px-4 py-3 ${model ? "border-model" : "border-line"}`}>
      <div className="text-xs uppercase tracking-wide text-muted">{label}{model ? " · model" : ""}</div>
      <div className={`num text-2xl font-medium whitespace-nowrap ${model ? "text-model" : ""}`}>{value}</div>
      {sub && <div className="num text-xs text-muted overflow-hidden text-ellipsis whitespace-nowrap">{sub}</div>}
      {hint && <div className="text-xs text-muted">{hint}</div>}
    </div>
  );
}
```

- [x] **Step 3: Create the caveat component**

`web/src/components/Caveat.tsx`. One component, so the wording cannot drift between screens.

```tsx
export function Caveat() {
  return (
    <p className="text-xs text-muted">
      A contradiction is not an allegation. These are differences between two published
      documents; the reason for a difference is not stated in either of them.
    </p>
  );
}
```

- [x] **Step 4: Create the CSV download button**

`web/src/components/CsvButton.tsx`. Takes already-shaped rows, builds a Blob, triggers a download. No new dependency.

```tsx
export function CsvButton({ rows, filename }: { rows: Record<string, unknown>[]; filename: string }) {
  function download() {
    if (!rows.length) return;
    const cols = Object.keys(rows[0]);
    const esc = (v: unknown) => {
      if (v == null) return "";                  // NULL stays empty. Never 0, never "NA".
      const s = String(v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  }
  return <button type="button" onClick={download}
    className="rounded border border-line px-2 py-1 text-xs hover:bg-ground">Download this table (CSV)</button>;
}
```

- [x] **Step 5: Restructure Overview**

Match `#/` in the reference mockup:

1. **Verdict block first**, above the tiles: an eyebrow naming the snapshot range, a sentence built from `findings.meta.headline.contradictions_arithmetic`, then `<Caveat />`. The number comes from JSON; only the sentence is a template.
2. **Eight tiles** using `croreShort` for `value` and `crore` for `sub` on the two currency tiles. `Statistical anomalies` and `Watchlist` pass `model`.
3. **Contradiction-type bars** from `findings.contradictions.by_type`: arithmetic types first sorted by count, `STAT_ANOMALY` separated below a rule, drawn in the model colour, carrying the word "model".
4. **Sector table** from `findings.by_sector`, with a footnote stating it is an agency-string rollup, not the 17 official ministries.
5. **Top-20 table sorted by `p.ml.slip_prob` descending**, with the rule band as a badge rather than a numeric column. This kills the twenty-identical-`100` column from spec section 2.3.
6. `<CsvButton>` on the table.

- [x] **Step 6: Build, screenshot, check**

```bash
cd web && npm run build && cd .. && python tools/routes.py
```

Screenshot `#/` at 1440x900 and check all six conditions in `docs/SCREEN-CHECKLIST.md`. Attach the screenshot to the task.

- [x] **Step 7: Gates and commit**

```bash
python tools/validate.py && pytest -q
git add web/src web/dist docs/superpowers/plans/2026-09-09-agrim-corrections-and-surface.md
git commit -m "task 22: overview verdict, corrected tiles, shared caveat and CSV export"
```

Paste both outputs. `validate.py` enforces the web-code literal allowlist (`100`, `1000`, `200`, `404` only; pixel sizes written with `px`), so a failure here means a magic number crept in.

---

### Task 26: The Project evidence screen

**Files:** `web/src/components/ShapBars.tsx` (create), `web/src/components/Sparkline.tsx`, `web/src/components/SourcePage.tsx`, `web/src/screens/Project.tsx`.

**Interfaces:**
- Consumes: `projects[].flags[]` with `first_snapshot` and `occurrences` from Task 21; `projects[].ml.slip_top_factors[]`.
- Produces: `<ShapBars factors />`; `<SourcePage snapshot page inline? />`.

Open `#/project/705410` in the reference mockup first. This screen gets 30 of the 95 demo seconds and is the one thing no rival entry has.

- [ ] **Step 1: Fix the sparkline colour**

`Project.tsx` calls `Sparkline` with `color="#1E7B4F"` for expenditure. That is the `ok` token, so project 705410's collapse from ₹89,486.62 cr to ₹2,384.29 cr currently renders in the reassuring green. Use the ink token for the trend line and mark the two contradicting points in `--color-critical`. Colour encodes severity only; a trend line is not a severity.

- [ ] **Step 2: Give SourcePage an inline variant**

Add `inline?: boolean`. When true, render a `<figure>` containing `<img src={`/pages/${snapshot}/p${page}.png`} alt="...">` at full container width, plus a `<figcaption>` naming the report, the page and the value read off it. Keep the existing chip as the default so other screens are untouched.

- [ ] **Step 3: Create ShapBars**

Replace the inline `Math.min(96, Math.abs(f.contribution) * 60)}px` divs. Bars diverge about a zero line: positive right, negative left, widths normalised to the largest absolute contribution in the set, all in `--color-model`. Caption: right increases the predicted probability, left decreases it.

- [ ] **Step 4: Promote the evidence block**

Pick the highest-severity flag (`critical` > `high` > `medium` > `low` > `info`, ties broken by earliest `first_snapshot`) and render it **full width above everything else**: the `detail` sentence in display type, `<Caveat />`, then both `sources[]` page images side by side via `<SourcePage inline />`. Everything currently on the page moves below it at lower visual weight. One focal point, not six equal cards.

- [ ] **Step 5: Show collapsed flags honestly**

A flag with `occurrences > 1` renders its month range — `2026-04 → 2026-07 · 4 reports` — and lists every page in `sources[]`. One persisting condition, one row.

- [ ] **Step 6: Build, screenshot, check, commit**

```bash
cd web && npm run build && cd .. && python tools/routes.py
python tools/validate.py && pytest -q
git commit -am "task 26: project evidence block, shap bars, severity-neutral sparklines"
```

Screenshot `#/project/705410` and check the six conditions. Paste both gate outputs.

---

### Task 27: Exits, and surfacing the new findings

**Files:** `web/src/screens/Exits.tsx`, `web/src/screens/Warning.tsx`, `web/src/screens/Drivers.tsx`, `web/src/screens/Fields.tsx`.

**Interfaces:**
- Consumes: `findings.delay_series` (Task 23), `findings.escalation` (Task 25), `findings.field_audit.whipple_index` and `.whipple_band` (Task 21).
- Produces: nothing other tasks depend on.

Open `#/exits` in the reference mockup first.

- [ ] **Step 1: Exit Ledger**

Add the explanatory paragraph from the mockup: rows are classified only by the last physical progress the reports actually showed, and no row is described as cancelled. Make the partition chips **neutral** — a project last seen at 98% that then vanished is arguably the most suspicious row on the screen, so no band may be coloured as success. Scale the pair bars to `max(exited, entered, commissioned_printed)` across `findings.exits.pairs`, never to a hardcoded ceiling. Add `<CsvButton>`.

- [ ] **Step 2: Early Warning gains the reconstructed delay series**

Render `findings.delay_series.rows` as a small multiple across the five snapshots with the five bands, and print `doc_null` beside every row as the excluded-for-NULL denominator. One interpretive sentence above it: these are the bands the Flash Reports used to publish, recomputed from the fields they still publish. Continuity-of-series reconstruction, never an accusation.

- [ ] **Step 3: Drivers gains the escalation matrix**

Render `findings.escalation.rows` as a table: rollup key, classifiable, delayed, delay rate, direction of travel, escalate flag. Read the threshold from `findings.escalation.threshold_pct`, never typed in. Footnote that the key is an agency-string rollup, not the 17 official ministries. **Cite no committee report number or date** — the attribution is unresolved per spec section 3.4, and the finding stands on the counts.

- [ ] **Step 4: Field Audit names its statistic**

Call out `whipple_index` and `whipple_band` beside the terminal-digit histogram, with one line explaining that Benford's Law does not apply to a bounded 0–100 progress field and that Whipple's index is the conventional measure for digit heaping.

- [ ] **Step 5: Build, screenshot all four, check, commit**

```bash
cd web && npm run build && cd .. && python tools/routes.py
python tools/validate.py && pytest -q
git commit -am "task 27: exit ledger caveats, delay series, escalation matrix, whipple index"
```

Screenshot `#/exits`, `#/warning`, `#/drivers` and `#/fields`. Check the six conditions on each. Paste both gate outputs.

---

### Guard for every screen task

Tasks 16–18 shipped a `web/dist` that runs offline today. A screen task can regress a working demo, so before starting one, note the current commit; `git checkout main -- web/dist` restores a working build. Run these before calling any screen task done:

```bash
grep -rEoh "https?://[^\"' )]+" web/dist/assets/*.js web/dist/assets/*.css web/dist/index.html | sort -u
grep -rEn "1775|1101|967|443|1289|3710641|340503" web/src/ | grep -v "\.json"
grep -rniE "air.?gap|auditor general|gov node|session key|sha-?verified|secrecy|official use only|agency portal" web/src/
grep -rnE "viewbox=|preserveaspectratio=|lineargradient|radialgradient|stop-color=" web/src/
```

Every one must return **no output**. The first proves the demo still runs with Wi-Fi off; the second enforces AGENTS.md rule 4; the third keeps the fabricated institutional authority from the mockups out of the build; the fourth catches lowercased SVG attributes that fail silently in JSX.

Then confirm the contract guard still fires: corrupt `web/dist/data/findings.json`, reload, and the app must refuse to render and name the failing key (D20). Restore it afterwards.

---

## Self-review notes

- **Spec coverage.** §2.1 → Task 21 Steps 10–11. §2.2 → Task 21 Steps 1–4. §2.3, §2.4 → Task 22 via the brief and checklist conditions 1, 2, 3, 5. §2.5 preserved: `detect()` is untouched and Task 21 Step 9 asserts it. §5 Task 21 items 1–4 → Task 21. §5 Task 22 → Task 22. §5 Task 23 → Task 23. §5 Task 24 → Task 24. §5 Task 25 → Task 25. §6 order → §Order. §7 → the gate step of every task. §8, §9, §10 are Window 2 and reference material, no task.
- **Deviation from the spec, recorded.** The spec's Task 24 called for `tools/shots.py` capturing screenshots. That needs a headless browser, which means a runtime download (AGENTS.md rule 7) and a lock re-freeze (rule 9). Replaced with `tools/routes.py`, which serves and enumerates while a human or agent screenshots. Same arbiter, no dependency.
- **Deviation from the spec, recorded.** The spec's Task 22 was one task covering the whole surface. Because tasks 16-18 already built all ten screens, and because the work is done in-repo rather than handed out, it is split into three subagent-sized tasks: 22 (shared primitives and Overview), 26 (Project evidence screen), 27 (Exits plus surfacing the Task 21/23/25 fields).  stays as internal reference for the data contract and route table.
- **Added after the spec, recorded.** Three external mockups were reviewed; see §Mockup corrections. Their layout ideas are adopted (two-panel evidence cockpit, abbreviated-plus-full currency tile, contradictions/anomalies split, exit-ledger caveat paragraph, panel chronology). Six defect classes are fixed in `docs/mockups/agrim-reference.html`, which becomes the visual target for Task 22.
- **Type consistency.** `classify(doc_original, doc_revised, snapshot)` is defined in Task 23 Step 3 and consumed with the same signature in Task 25 Step 3. `collapse(flags)` is defined in Task 21 Step 3 and consumed in Task 21 Step 11 only. `whipple_index`/`whipple_band` are defined and consumed inside Task 21.
- **Contract version chain.** 1.0.0 → 1.1.0 (Task 21) → 1.2.0 (Task 23) → 1.3.0 (Task 25). Each task bumps `CONTRACT_VERSION` in `findings/run.py` and adds a `CHANGELOG.md` entry.
