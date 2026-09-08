# AGRIM — surface, corrections and phase 2 — design

**Date:** 8 September 2026
**Status:** approved for implementation. Extends `docs/BUILD.md` and the relay plan; supersedes nothing.
**Gates:** internal round Saturday 12 September 2026 (Window 1). National idea submission, portal deadline 30 September 2026 (Window 2).

Tags follow BUILD.md: **[verified]** = command run or page opened by this session; **[from research]** = agent report with a primary or near-primary source; **[unverified]** = a claim stated so it can be challenged, to be checked before it reaches a slide.

---

## 1. Why this spec exists

The pipeline is ahead of schedule and the surface is behind it. Tasks 1–17 are committed (branch `claude/repo-status-check-632b01`, task 17). Tasks 18, 19 and 20 remain, and `deck/` contains only `numbers.json`. **[verified]**

Running the task-17 build surfaced three defects in published numbers and a set of layout problems, none of which are visible from reading the code. This spec fixes those, adds three findings modules the competitive research showed to be unoccupied ground, and installs the verification loop the surface has never had.

It does not change the architecture. D11 holds: no server, no API, build-time JSON into `web/public/data/`, demo runs offline from `RUN_DEMO.bat`.

---

## 2. What running the build showed

Served `web/dist` from the task-17 branch at 1440×900 and walked `#/`, `#/project/705410` and `#/predict`. **[verified]**

### 2.1 The contradictions headline blends rule-based and model-based findings

The Overview KPI reads "Contradictions · 1,101 · arithmetic impossibilities". Counting flag types in `projects.json`: **[verified]**

```
EXP_GT_REVISED_COST     331
ZERO_PROG_NONZERO_EXP   285
EXP_DECREASE            185
PROG_DECREASE           158
STAT_ANOMALY            134   <- M4 isolation forest
DOC_BEFORE_APPROVAL       8
                       ----
                       1101
```

134 of the 1,101 are model output, not arithmetic impossibilities. This violates the spirit of D42 ("the rule-based risk score stays separate from the model probability; both columns are shown, never blended") and contradicts BUILD.md §8, which orders `STAT_ANOMALY` last in the ledger precisely because it differs in kind. A sponsor representative who asks to see an arithmetic impossibility and lands on a statistical outlier damages the honesty framing the whole pitch rests on.

**The word "impossibilities" also overreaches, and Task 21 must resolve it.** Only `EXP_DECREASE` (185) and `PROG_DECREASE` (158) are true impossibilities — a cumulative field cannot fall. `EXP_GT_REVISED_COST` (331) can occur legitimately when an agency overspends against an unrevised sanction; `ZERO_PROG_NONZERO_EXP` (285) is normal during land acquisition and mobilisation; `DOC_BEFORE_APPROVAL` (8) is a data-entry contradiction rather than an arithmetic one. So the honest split is **343 impossibilities and 624 contradictions or implausibilities**, not 967 impossibilities. Pick the wording that survives a hostile question and use it on every screen, in `deck/numbers.json`, and in the pitch.

### 2.2 22% of flags are the same flag repeating

Of 4,661 flags, 1,031 are a repeat of the same flag type on the same project in a later snapshot. **[verified]** On `#/project/705410` this renders as four near-identical rows reading "Cumulative expenditure ₹2,398.08 cr exceeds the revised cost ₹2,018.00 cr" for 2026-04 through 2026-07. It is one persisting condition printed four times. It buries the genuinely dramatic flag on the same page — expenditure falling from ₹89,486.62 cr to ₹2,384.29 cr — and inflates every count derived from flags.

### 2.3 The landing screen's rule-risk column carries no information

Overview sorts the top 20 by rule risk, so every visible row reads `red · 100`. The score itself is healthy: only 23 of 2,128 projects reach 100, and the modal scores are 40, 50, 25 and 60. **[verified]** The defect is in the view, not the model — the default sort makes the column constant on the first screen a judge sees. The adjacent model probability column ranges from 93% down to 6% and is doing all the discriminating.

### 2.4 Layout defects

- KPI tiles are too narrow for Indian-formatted currency; `₹ 37,10,641.55 cr` wraps across three lines. **[verified]**
- The Project page expenditure sparkline draws the ₹89,486 cr → ₹2,384 cr collapse in `#1E7B4F`, which is the `ok` token. BUILD.md §8 states colour encodes severity only, never decoration. A collapse currently renders in the reassuring colour. **[verified]**
- Every panel on the Project page is the same `rounded border border-line bg-surface p-3` card, in three consecutive two-column grids. The "As printed, by report" table, the strongest evidence artifact on the page, carries the same visual weight as a collapsed accordion. **[verified]**

### 2.5 What is already right, and must not be "improved"

- `findings/field_audit.py` uses terminal-digit clustering and multiple-of-5/10 shares, **not** Benford's Law. Benford is invalid on bounded 0–100 progress data. This is correct, and is a point of superiority over rivals who will reach for Benford. **[verified]**
- The Predictions screen already shows logistic regression beside gradient boosting beside a shuffled-label control (PR-AUC 0.347 / 0.605 / 0.203), with PR and calibration curves and an honest caveat line. It needs polish, not rework. **[verified]**
- The design tokens — IBM Plex Sans/Mono, tabular numerals, institutional palette, `--color-model: #5B4B9A` reserved for model-derived numbers — are sound. **[verified]**

---

## 3. Competitive position

### 3.1 The model stack is no longer the differentiator

A GitHub search for `SIH26103` returns 19 repositories. The most developed one inspected uses React 19 + FastAPI with Random Forest, XGBoost, Isolation Forest and SHAP, a what-if simulator and GIS heatmaps — but its data comes from `database/seed_data.py` and is synthetic. Others are placeholder files, or a single-file React page with ten hardcoded projects. **[from research]**

A separate live prototype self-labelling "Smart India Hackathon 2026 / Problem Statement: SIH26103" advertises a 100-point risk score, peer velocity benchmarking, a what-if policy simulator, GIS mapping, geo-tagged progress photographs and a "Public Citizen Auditor" role; its dashboard metrics currently render as placeholder zeros. **[from research]**

**Consequence:** isolation forest, SHAP and a dashboard are the modal SIH26103 answer. AGRIM's defensible moat is the five real parsed Flash Reports at 95–100% coverage plus out-of-time validation on a report the model never saw (D32). That leads the pitch; the model list does not.

### 3.2 The incumbent has publicly deferred exactly what AGRIM does

PAIMANA replaced OCMS-2006 and is NIC-built on MS SQL / NIC Cloud with a Bootstrap frontend and SSRS dashboards, pulling over 70% of project data automatically from DPIIT's IPMP via API. The NIC technical writeup lists AI-driven forecasting and machine learning for time and cost overrun prediction as **future** enhancements, and contains no mention of GIS, geo-tagging, photographs or geospatial mapping. There is no public risk scoring, no alerting and no citizen complaint channel. **[from research]**

### 3.3 The discontinued delay series

Flash Reports compared across 25 years: April 2001 flagged 32% of 191 projects as delayed. April 2014 named 282 of 727 projects explicitly behind schedule, bucketed into up to 12 months, 13–24, 25–60, and beyond 61 months, with documented delay reasons. April 2026 does not use the word "delay" at all, substituting physical-progress bands. **[from research]**

This is the strongest available contribution: the classification was discontinued, the underlying fields are still published, and AGRIM already parses them.

### 3.4 A parliamentary recommendation nobody has implemented

The Standing Committee on Finance recorded 1,105 of 1,702 projects delayed (65%) as of 31 January 2026, and recommended MoSPI operationalise a "structured escalation matrix" — dynamically calibrated, flagging ministries whose delay rate exceeds 50% with no year-on-year improvement, for escalation to the Cabinet Secretariat / PMO for PRAGATI review. **[from research]**

**Attribution conflict.** `docs/BUILD.md` §2 dates this to Business Standard, 11 August 2026. The research dates it to the 35th Report, 17 March 2026, via Outlook Business. The figures agree; the source does not. **[unverified]** Task 25 must not quote a date or report number until one is confirmed; the finding stands on the numbers alone until then.

### 3.5 The photo and complaint layer is out of scope for the build

Rejected for Window 1 and for the Window 2 build, in its collect-photos form, on three grounds:

1. **Not novel.** Bhuvan (NRSC/ISRO) already runs geo-tagged photo capture for MGNREGA at three construction stages, with block-level GIS supervisor validation and public publication, past one crore assets — plus PMAY-G's AwaasApp, which gates instalment release on foundation / lintel / roof photographs. **[from research]**
2. **Not a differentiator here.** A rival SIH26103 prototype already ships geo-tagged photographs and a citizen auditor role. **[from research]**
3. **Documented to fail, from primary audit text.** CAG, Audit Report (Local Bodies) for the year ended March 2017, Chapter II, on Bhuvan geo-tagged photographs: in one gram panchayat "same photograph was uploaded for two different works", and in three others "the photograph uploaded in the portal was different from the actual worksite", concluding "This indicated that the MIS data was unreliable." Separately, photographs were missing on 4.33 lakh job cards across seven states, and the Ministry of Rural Development added manual physical verification behind NMMS app photos in July 2025 after documented misuse. **[from research, quoted verbatim from the CAG PDF by the research agent]**

**The surviving form, for Window 2 as a concept slide only:** photo *integrity* rather than photo collection — duplicate-image detection, EXIF and geo cross-validation, and reconciliation of existing scheme photo evidence against reported physical progress. No deployed system links field photographs back to financial and physical progress reconciliation. This is a slide, not a build, and it carries the CAG finding as its justification.

---

## 4. Scope

**In scope, Window 1 (now → Friday 11 September):** new tasks 21–25, appended to `docs/superpowers/plans/2026-09-06-agrim-relay-plan.md`, plus existing tasks 18, 19 and 20 unchanged.

**In scope, Window 2 (13 → 30 September):** sketched in §8, specced separately once Window 1 is committed.

**Explicitly out of scope:** any server, API or database before 12 September (D11); photo capture or complaint intake in any form; redesign of the token system; changes to the parser, to `panel.csv`, or to any model in `findings/models/`; retraining or re-tuning — M1–M4 outputs are frozen as committed at task 14.

---

## 5. The tasks

Each task names the files it may edit. AGENTS.md rule 1 applies: edit only those files plus tests. AGENTS.md rule 2 is relaxed only where a task names a contract file, and only additively per D29 — new fields must be nullable, with a minor version bump recorded in `contracts/CHANGELOG.md`.

### Task 21 — Findings corrections

**Files:** `findings/contradictions.py`, `findings/field_audit.py`, `findings/run.py`, `contracts/findings.schema.json`, `contracts/projects.schema.json`, `contracts/CHANGELOG.md`, `tests/`.

1. **Split the contradictions headline.** `findings.meta.headline` gains `contradictions_arithmetic` — the five non-anomaly types, expected 967 — alongside the existing `contradictions_total`. `STAT_ANOMALY` is reported only through its own count. Additionally, per §2.1, emit `impossibilities` (expected 343, the two cumulative-decrease types) separately from the remaining 624, and settle the on-screen wording. No existing field is removed or redefined.
2. **Collapse repeated flags.** Where the same flag `type` recurs for the same project in consecutive snapshots, emit one flag carrying `first_snapshot`, `last_snapshot` and the union of all `sources[]` page citations. Every citation survives; no page reference is lost. Counts derived from flags fall accordingly, and every dependent number is regenerated.
3. **Denominator counts.** For each headline figure, emit the count of projects excluded because the field it depends on is NULL. AGENTS.md rule 3 already guarantees NULL means "not printed", so this is a count, never an inference.
4. **Whipple's index.** Compute the standard index over the terminal-digit distribution `field_audit.py` already produces, and emit the index value plus its UN quality-band label as a string. Naming a conventional statistic is part of the answer to PS dimension (b); no new statistical method is introduced.

**Done when:** `python tools/validate.py` exits 0 and `pytest -q` passes, both pasted; the double-run diff is clean; `deck/numbers.json` is regenerated.

### Task 22 — Surface hierarchy and the two signature moments

**Files:** `web/src/screens/Project.tsx`, `web/src/screens/Overview.tsx`, `web/src/components/Sparkline.tsx`, `web/src/components/KPI.tsx`, `web/src/index.css`, `web/src/lib/format.ts`.

**Signature moment one — the Project page evidence block.** The highest-severity flag is promoted out of the list into a full-width block at the top of the page: the flag sentence in display type, the rendered PDF page image inline at readable size rather than behind a chip, and the parsed value called out beside it. Sparklines, remaining flags, the Outlook card, the brief and the as-printed table all drop to secondary weight below it. The page must have one focal point, not six equal cards.

**Signature moment two — the Overview verdict.** The seven-tile grid is replaced by a stated finding in sentence form, followed by the arithmetic contradiction types as a ranked bar, then the map slot, then the table. Tiles that survive are wide enough that `₹ 37,10,641.55 cr` occupies one line.

**Corrections.** Overview's default sort moves to model probability, with the rule band shown as a chip rather than a constant numeric column. Sparklines use severity-neutral ink; the `ok` token is never used for a trend line.

**Two additions, both cheap, both borrowed from audit practice:**

- A fixed caveat wherever flags appear: **a contradiction is not an allegation.** Modelled on ICIJ Offshore Leaks, which states plainly that duplicates are possible and that many listed activities are perfectly legal. **[from research]**
- A "download this table as CSV" affordance on every table, reusing the D43 review-pack export path. Modelled on the UK National Audit Office, which publishes raw CSV alongside every visualisation. **[from research]**

**Done when:** every route passes the Task 24 checklist with its screenshot attached to the task, and `python tools/validate.py` exits 0.

### Task 23 — Delay-series reconstruction

**Files:** new `findings/delay_series.py`, `findings/run.py`, `contracts/findings.schema.json`, `contracts/CHANGELOG.md`, `tests/`, plus one screen section in `web/src/screens/Warning.tsx`.

Reconstruct the classification MoSPI discontinued, using the government's own April 2014 bucket boundaries: on schedule, and delayed by up to 12 months, 13–24 months, 25–60 months, and 61 months or more, measured against each project's stated completion date. Use the 2014 wording for the bands verbatim, so the series is visibly the same series. Compute for all five snapshots so the series has a trajectory, and print the excluded-for-NULL denominator beside every band, since projects with no stated completion date cannot be classified at all.

Framing is fixed and non-negotiable: **continuity-of-series reconstruction, never an accusation.** The sponsor is in the room. The sentence is "these are the bands the report used to publish, recomputed from the fields it still publishes" — not "they hid the delays".

**Done when:** validate and pytest pass and are pasted; the band counts sum to the classifiable project count; the NULL-excluded count is emitted.

### Task 24 — The visual arbiter

**Files:** new `tools/shots.py`, new `docs/SCREEN-CHECKLIST.md`, `.gitignore`.

Tasks 1–17 had `tools/validate.py` and `pytest -q` as arbiters and came out disciplined. The screens had neither and came out uniform. This installs the missing loop.

`tools/shots.py` serves `web/dist`, captures every route at 1440×900, and writes PNGs to a gitignored directory. `docs/SCREEN-CHECKLIST.md` is the pass condition, and a screen task is not done until its screenshot has been checked against it:

1. No number wraps across lines.
2. No column shows the same value in every visible row.
3. Colour encodes severity only; no colour used decoratively.
4. Every model-derived number is in `#5B4B9A` and carries the word "model".
5. The screen has exactly one focal point.
6. Every displayed figure traces to a page citation, or is explicitly labelled model-derived.

Build this before Task 22, so Task 22 is the first screen work it governs.

### Task 25 — Escalation matrix

**Files:** new `findings/escalation.py`, `findings/run.py`, `contracts/findings.schema.json`, `contracts/CHANGELOG.md`, `tests/`, plus one screen section in `web/src/screens/Drivers.tsx`.

Implements the Standing Committee's recommendation. Per ministry or agency rollup: delay rate from Task 23's bands, the direction of travel across the five snapshots, and a flag where the delay rate exceeds 50% with no improvement over the observed window. Output is a ranked table showing the flag and the underlying counts.

Two constraints. Sector and ministry attribution rests on D15's agency-string rollup, which is a rollup and must say so on screen — no NLP mapping to the 17 ministries before the round. And per §3.4, no Committee report number or date is cited until the attribution conflict is resolved.

### Tasks 18, 19, 20 — unchanged

As written in the relay plan: assistant, model card, India map, review-pack export, demo runner and committed build (18); cached grounded LLM briefs (19); deck, pitch, rehearsal and release tag (20).

---

## 6. Order and the cut line

| When | Work | Gate |
|---|---|---|
| Tonight → Wed 9 | Tasks 21, 23, 25 — all in `findings/` | Full pipeline run. `validate.py` and `pytest -q` output pasted. `deck/numbers.json` regenerated. **Numbers frozen Wednesday night.** |
| Wed 9 evening | Task 24 | Checklist written, `tools/shots.py` runs |
| Wed 9 → Thu 10 | Task 22, then existing Task 18 | Every route screenshot-checked against the checklist |
| Thu 10 evening | Existing Task 20 — deck and pitch, against frozen numbers | Six slides in the unaltered official template, exported to PDF once |
| Fri 11 | Existing Task 19 if green. Cold-machine rehearsal twice on a second laptop with Wi-Fi off. Three timed pitch runs. | Bug fixes only |

**Cut line, decided now.** Extends D41 rather than replacing it.

- **Wednesday 22:00.** If Task 23 or Task 25 is not producing a number you would defend to a MoSPI officer, it is dropped and becomes a "next step" slide. Neither is allowed to delay the numbers freeze.
- **Thursday 22:00, in this order:** Task 19 briefs → Task 18's India map → Task 22's CSV-export affordance.
- **Never cut:** Task 21, Task 22's Project evidence block, the deck, the cold-machine rehearsal.

The deck must not depend on Task 23 or Task 25 landing. It is written against whatever `deck/numbers.json` contains at the Wednesday freeze, with the reconstructed-delay slide included only if the number exists by then.

---

## 7. Verification requirements

Non-negotiable, from AGENTS.md:

- **Rule 8.** `python tools/validate.py` and `pytest -q` run and pasted before any task is called done. No task claims completion on a described run.
- **Rule 3.** Empty CSV cell = NULL = "not printed". The denominator counts in Tasks 21 and 23 exist to make this visible, never to substitute a zero.
- **Rule 4.** No number that comes from the data is hardcoded anywhere. The reconstructed delay counts and the escalation flags reach the deck through `deck/numbers.json` only.
- **Rule 5.** Determinism. Every addition in Tasks 21, 23 and 25 is deterministic arithmetic; the validator's double-run diff must stay clean.
- **Rule 11.** Plan checkboxes ticked and committed with the code. **Rule 12.** Commit messages `task NN: <what>`.

**One verification action outside the tasks, worth doing first.** The research could not open any Flash Report PDF — the archive host's certificate is expired and PIB returns 403 to automated fetches. You have all five committed in `data/pdfs/`. MoSPI's reports reportedly carry a standing caveat that project agencies are not reporting revised cost estimates and commissioning schedules for many projects, so time and cost overrun figures may be under-reported. **[unverified]** If that sentence is present, it is the sponsor conceding the problem in its own document, citable to a page you can already render, and it belongs in the pitch. Confirm before quoting.

---

## 8. Window 2 — sketch only

Specced separately once Window 1 is committed. Four candidates, ranked:

1. **The six-slide national PDF**, positioned against PAIMANA's own published roadmap: the incumbent has scheduled AI-driven forecasting and ML overrun prediction and has not shipped them.
2. **AGRIM's panel as an MCP server**, mirroring MoSPI's own open-sourced eSankhyiki MCP server (MIT, February 2026). **[from research]** The most on-brand available form of outcome (h) — the sponsor has already committed to AI-ready structured access to its statistics — and no rival repository inspected does it.
3. **The parsed panel committed as a citable open dataset.** No published academic panel analysis of this data was found, so the dataset is itself a contribution. **[unverified — absence of evidence, not evidence of absence]**
4. **Photo integrity as a concept slide**, per §3.5: duplicate detection, EXIF and geo cross-validation, and reconciliation of existing scheme photo evidence against reported physical progress, justified by the CAG finding.

---

## 9. Design references

For Task 22 and the Window 2 redesign. Each named with the one thing to take from it. **[from research]**

| Reference | What to take |
|---|---|
| Reuters Graphics style | Categorical, sequential and diverging palette discipline as a system |
| FT Visual Vocabulary | Choose chart form by relationship — deviation, ranking, magnitude, change over time. Removes the donut reflex. |
| GOV.UK brand data guidance; ONS Design System | Statistics-publishing chrome, zero baselines, cite-the-source as a stated principle |
| National Audit Office (UK) | Publishes raw CSV alongside every visualisation — adopted in Task 22 |
| ICIJ Offshore Leaks | Explicit caveat that records are not allegations — adopted in Task 22 |
| NYT Upshot annotation doctrine | One interpretive sentence per chart, never bare data |
| Tufte small multiples; Linear chrome density | Per-ministry league tables; tight padding, small radii |

**Tells to avoid** — the failure mode here is unarbitrated generation rather than bad taste: purple-to-cyan gradients, glassmorphism, oversized rounded cards, a hero section inside a dashboard, KPI grids that fill space without supporting a task, bounce or scale hover animation, emoji. BUILD.md §8 already bans animation beyond 150–200 ms; Task 24 enforces the rest.

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Numbers change under a half-written deck | Single freeze Wednesday night; deck written Thursday against frozen `deck/numbers.json` only |
| Tasks 23 and 25 are new modules four days out | Both are deterministic arithmetic on already-parsed fields — no model, no new dependency — and both sit behind a Wednesday 22:00 cut |
| Contract edits after the D29 freeze | Additive nullable fields only, minor bump, `CHANGELOG.md` entry per task |
| Flag collapse silently drops a page citation | `sources[]` is the union of all collapsed occurrences; a test asserts citation count is preserved |
| Standing Committee attribution is contradictory | Task 25 cites no report number or date until resolved; the finding stands on the counts |
| Reconstructed delay series reads as an attack on the sponsor | Framing fixed in Task 23: continuity-of-series reconstruction, stated on screen and in the pitch |
