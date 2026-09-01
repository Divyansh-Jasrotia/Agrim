# AGRIM — Build Document v2 (5 September 2026)

**Status:** decisions, not context. Every choice below is final for the 12 September internal round unless Ranvir overrides it. Each decision carries a one-line *why* so any team member can defend it in a review. Tags: **[verified today]** = command run or page opened on 5 Sept 2026; **[from research]** = agent report with a primary source; **[assumed]** = a call made without evidence, stated so it can be challenged.

**What changed from v1:** the predictive layer is now in scope for 12 September, because the problem statement makes AI/ML prediction and the AI-vs-conventional comparison a core expectation, not an option. Four models, one LLM component, three new screens, and a tool-by-tool guide for working with three different AI coding tools were added. Nothing from v1 was removed; the audit layer is still the headline fact and the models are now the second beat of the pitch instead of a slide.

**Companion:** `AGRIM-context.md` (the facts and the analysis history). This file does not repeat it.

**Plan-time amendments (6 Sept 2026, recorded when the implementation plan was written; the plan wins where they differ):**
- **Work model:** the team chose a sequential relay over parallel directory ownership. Twenty ordered tasks in `docs/superpowers/plans/2026-09-06-agrim-relay-plan.md`; anyone picks up from the last ticked checkbox; claims and handoffs are logged in `docs/RELAY.md`; the reviewer of Task N is whoever does Task N+1. §5's per-person ownership and §10's per-person schedule are superseded by the plan's task order; §11.6's tool guidance still applies per task.
- **D16:** shadcn/ui dropped; Tailwind v4 plus four hand-written components (Badge, KPI, DataTable, Sparkline). Reason: an interactive CLI and dozens of generated files are wrong for a relay with mixed AI tools.
- **D20:** Ajv validates the `contracts/*.schema.json` files directly in the browser and `json-schema-to-typescript` generates the TypeScript types; Zod is not used. Reason: one schema source for Python and TypeScript, nothing to drift.
- **D19:** TanStack Table pinned to v8 (the API the plan's code uses); react-router-dom pinned to v6.
- **Layout:** tests live under `tests/` at the repo root; page images under `web/public/pages/`; `web/dist` is committed so the demo laptop needs no Node; `data/aggregates.json` (page-3 totals) lives under `data/`, keeping `contracts/` untouched outside Tasks 2 and 9.
- **Validator allowlist:** `100`, `1000`, `200`, `404` are permitted literals in web code (arithmetic constants and HTTP codes), and pixel sizes must be written with `px`.

### 0.1 How to use this document

| Who | Read | Paste into your AI tool at every session start |
|---|---|---|
| Lead (Ranvir) | all of it | — |
| P (parser, drivers model, briefs) | §0–1, §3.1–3.2, §4, §5.1, §6.1, §7B (M3, briefs), §10, §11 | `AGENTS.md` + §5.1 + §6.1 + the M3/briefs part of §7B |
| A (findings, prediction models) | §1, §3.3, §5.2, §6, §7, §7B, §10, §11 | `AGENTS.md` + §5.2 + §6 + §7 + §7B |
| S (dashboard, deck, pitch) | §1, §3.4, §5.3, §6.2–6.3, §8, §9, §10, §11 | `AGENTS.md` + §5.3 + §6.2–6.3 + §8 |

The one rule: the files in `contracts/` and the output of `python tools/validate.py` decide what is correct. Not the agent, not the person, not this document's prose.

---

## 0. Calibration — read this before anything else

| | |
|---|---|
| **Gate** | Internal college round, 12 Sept 2026: 3-minute pitch + PPT, prototype optional. Rewards problem understanding and innovation (about half the score in the five published college rubrics found), feasibility (a fifth to a quarter), presentation (a tenth to a fifth). **[from research]** |
| **Base rate** | Internal rounds pass anywhere from 9% (583-team university) to 70% (50→35 teams) depending on college size. National shortlist ≈ 2% (SIH 2025: 5 slots per PS, ~266 ideas per PS). |
| **This entry, internal round** | 70–85% if the demo runs on real data, the opener lands, and the model-comparison table is on screen. Moved most by whether the panel rewards an audit finding plus an honest model, or counts buzzwords. |
| **This entry, national screening** | 8–14% as framed (vs 2% base). First-ever SIH problem statement on this data, 0/500 idea counter on 5 Sept, a verified data moat, and now every enumerated outcome (a)–(i) visibly addressed. Moved most by the six-slide PDF. |
| **Saturation** | High for "AI dashboard + gradient boosting + SHAP + LLM assistant", which is what the modal rival will submit. Our version of the same words differs in three checkable ways: out-of-time validation on the sponsor's own next report, the conventional baseline shown even where it wins, and the positives count printed next to every metric. |

**Two dates:** guidelines PDF says idea submission closes **15 Sept**; the live portal now shows **30 Sept** for every PS (it showed 20 Sept last week). **[verified today]** Plan to 15 Sept. Ask the SPOC (item 14.1).

---

## 1. What we are building for 12 September

**One sentence:** a reporting-integrity audit and an early-warning prediction layer over MoSPI's own monthly project panel, computed from five public Flash Report PDFs (Dec 2025, Apr–Jul 2026), validated out-of-time on the newest report, shown as a live offline dashboard.

**Deliverables, ranked by what the gate scores:**

1. **The 3-minute pitch** (script in §9, one presenter, one operator).
2. **The six-slide deck** in the unaltered official template, exported to PDF (§9).
3. **The prototype**: one static web app on real data, run from a laptop with Wi-Fi off, showing the findings and models below.

**Audit layer — findings shipped as code (deterministic, no training set):**

| # | Finding | PS outcome it visibly covers | Needs |
|---|---|---|---|
| F1 | **Contradiction Ledger** — arithmetic impossibilities between consecutive reports (cumulative expenditure falls, progress falls, etc.) with PDF page citations | (e) benchmarking/comparative; (g) dashboard | 2 snapshots |
| F2 | **Exit Ledger** — projects that vanish between reports, with last-observed state; reconciled against the report's own "commissioned this month" count if the PDF prints it | (e), (g) | 2 snapshots |
| F3 | **Unreachable-DoC early warning** — at its own reported progress rate, can the project reach 100% by its own stated completion date? | (d) early-warning alerts | 2 snapshots (better with 4) |
| F4 | **Rule-based risk score** — transparent 0–100 composite of F1–F3 with a reasons list | (c) risk scoring framework | F1–F3 |
| F5 | **Field-Information Audit** — round-number and terminal-digit clustering of Physical Progress; per-agency staleness | dimension (c) of the PS | 1 snapshot |
| F6 | *(stretch, Day 5)* **Disclosure Lag** — for projects that filed a revised DoC in May–Jul, the earliest earlier month at which F3 already flagged them | (d) | 4+ snapshots |

**Prediction layer — models shipped as code (scikit-learn, deterministic, validated on the held-out July report):**

| # | Model | Question it answers | Conventional baseline shown beside it | PS outcome |
|---|---|---|---|---|
| M1 | **Slip-filing classifier** | Which projects will file a revised completion date in the next report? | Logistic regression on the same fields | (b) time-overrun prediction; (d) early warning; dimension (b) AI vs conventional; dimension (c) via feature-set A vs B |
| M2 | **Progress forecaster** | How much physical progress will each project report next month, and when will it reach 100%? | No-change and the project's own linear extrapolation | (b) time overrun in months; dimension (b) |
| M3 | **Overrun driver and peer-benchmark model** | What drives cost and time overrun across the panel, and how does each project compare with its peers? | OLS with the same features (Ram Singh 2009/2011 replication) | (e) benchmarking; (f) cost-escalation driver analysis |
| M4 | **Statistical anomaly detector** | Which month-to-month changes are unusual even when arithmetically possible? | The arithmetic rules of F1 | (e); strengthens the audit layer |

**LLM layer:** offline-generated, ledger-grounded **project briefs** for the top-risk projects (Ollama, small open model), each verified number-by-number against the fact sheet it was written from, cached as JSON, plus a **templated assistant** with eight fixed questions and a project-code lookup. A live free-text mode switches on only if the local model is running; it is never on the rehearsed demo path. Covers outcome (h).

**Documentation layer:** a **model card** screen (data, splits, positives, metrics, limitations, the CUF fields we cannot see) and a **Monthly Review Pack** CSV export. Covers outcome (i) and the operator framing.

**Explicitly NOT built before 12 Sept** (each is a slide, labelled "next step"): survival model with censoring (needs the 16-month archive), cost-escalation *forecast* (23 positives per 4 months cannot train anything defensible; cost stays a driver analysis), the 15-month archive on the expired-certificate host, WPI/IMD external series, NLP normalisation of agency strings to the 17 ministries / 22 sectors, live LLM as a dependency of any demo beat.

---

## 2. Facts established today (5 Sept 2026)

| Fact | Evidence |
|---|---|
| April 2026 Flash Report reachable, valid TLS, 6,543,938 bytes | `curl -I` → HTTP 200 **[verified today]** |
| December 2025 report reachable, 6,398,361 bytes; May 2024 (OCMS-era) reachable, 7,949,105 bytes | HTTP 200 **[verified today]** |
| **May, June, July 2026 reports exist on the valid-TLS mirror** (URLs in §3.1). August not published anywhere. | HEAD 200 on all three **[from research, host-check agent]** |
| ipm.mospi.gov.in certificate still expired (notAfter 29 Jun 2026); serves HTTP 200 with verification disabled; plain HTTP redirects to HTTPS | `curl` → `SEC_E_CERT_EXPIRED`; `curl -k` → 200 **[verified today]** |
| PAIMANA archive page links resolve to a 404 host; the working copies are on ipm (expired cert) or mospi.gov.in (hashed names) | **[from research]** |
| No PDFs and no parser survive on disk from the 1 Sept analysis; the 87% figure is from a transcript | `find . -iname *.pdf` → nothing **[verified today]** |
| Default `python` on this machine is **3.12.10** (not 3.13 as CLAUDE.md says); 3.13 Store build also present; uv 0.9.22, git 2.52, Node 24.15, npm 11.12 | `python --version` etc. **[verified today]** |
| Every Python package we need ships a Windows wheel for 3.12 and 3.13, including shap 0.52 and lifelines 0.30 | PyPI **[from research]** |
| SHAP `TreeExplainer` supports scikit-learn `HistGradientBoostingClassifier` and `Regressor` | shap test suite **[from research]** |
| scikit-learn docs do not state whether HistGradientBoosting is byte-identical across runs under OpenMP threading | docs read; absence noted **[from research]** — hence D36 |
| Ollama supports `options={"seed": n, "temperature": 0}` and `num_ctx`; health check `GET http://localhost:11434/` returns "Ollama is running" | Ollama API docs **[from research]** |
| Cursor project rules live in `.cursor/rules/*.mdc` with `description`, `globs`, `alwaysApply` frontmatter; legacy `.cursorrules` deprecated; Cursor reads a root `AGENTS.md` | Cursor docs; AGENTS.md claim from a secondary source **[from research]** |
| Claude Code loads root `CLAUDE.md` every session and it can import another file with `@AGENTS.md` | Claude Code docs **[from research]** |
| ChatGPT Projects carry instructions and files visible to every chat in the project (Free: 5 files; Plus: 25); code execution on uploaded CSVs is available on Free with rate limits; the GitHub connector is read-only | help.openai.com pages returned 403 to the agent; limits from secondary sources **[claimed]** |
| Official template: `SIH2026-IDEA-Presentation-Format.pptx` (903 KB) on sih.gov.in; six slides max including title; fixed headings; PDF upload only; "avoid paragraphs" | template XML read **[from research]** |
| No CAG, MoSPI, PRS, committee or press reconciliation of month-to-month arithmetic inconsistencies exists (11 searches). Closest: The Wire (29 May 2026) on the dropped "delayed projects" count; ABC Live scoring the portal 31/100 for "no anomaly flags" | **[from research]** |
| Pre-PAIMANA reports carried "Annexure III: projects in which expenditure is more than approved cost" | search snippet, not opened **[claimed]** |
| PIB releases for the March and April 2026 reports carry a section "Completed Projects and New Additions" with a commissioned count (Mar: 25; Apr: 9) | PIB PRIDs 2255270, 2264967 **[from research]** |
| Standing Committee on Finance, Aug 2026: 1,105 of 1,702 projects delayed as of 31 Jan 2026 | Business Standard 11 Aug 2026 **[from research]** |
| Panel counts by press/PIB: 1,981 (Apr) → 1,847 (Jun) → 1,775 (Jul) | **[from research]** |
| Dec 2025 ↔ Apr 2026: 599 of 1,150 matched projects changed Revised DoC; 23 changed Revised Cost | Phase-3 join, from `AGRIM-context.md` §3.4 **[claimed, transcript]** — this is why M1 targets DoC filings and no model targets cost |
| SIH26103 idea counter 0/500 on 5 Sept; SIH26103 is the first OCMS/PAIMANA PS in any SIH edition (2022–2025 lists searched) | **[from research]** |
| Ram Singh papers: open PDFs at cdedse.org/pdf/work181.pdf and econdse.org (EPW 2010); 894 projects, 17 sectors; data source named only inside the PDF | **[from research]** |

---

## 3. Decisions register

Each row: the decision, the reason a reviewer will accept, the evidence tag.

### 3.1 Data

| # | Decision | Why | Tag |
|---|---|---|---|
| D1 | **Snapshots in scope for 12 Sept: Dec 2025, Apr, May, Jun, Jul 2026** (five PDFs, all valid-TLS mospi.gov.in). Archive (Jan 2025–Mar 2026 on ipm) is Phase 3. | Four consecutive PAIMANA months give three one-month training pairs plus one held-out pair for the models, month-by-month exits, and a four-point progress trajectory. Dec 2025 adds a fourth training pair and the 23-month join spine. | verified |
| D2 | **Commit the PDFs and a `SHA256SUMS` file to the repo.** No Git LFS. | ~33 MB total; makes "demo machine has no data" impossible; LFS is one more install to fail. | assumed (size arithmetic) |
| D3 | **Download once, by script, never at runtime.** `tools/fetch_pdfs.py` with pinned URLs and checksums. | The archive host's certificate is expired and file names are opaque hashes; a live fetch on stage is a demo killer. | verified |
| D4 | **Canonical store is `data/out/panel.csv`, long format, one row per (snapshot, project).** DuckDB/Parquet are private tools of the Findings person, not the contract. | CSV is diffable in git, readable by any agent, needs no wheel. | — |
| D5 | **The parser never derives.** No overruns, deltas, sectors, or joins in `panel.csv`. `NULL` (empty cell) means "not printed", never 0. | Kills duplicated logic between components; the prior stitching failure was exactly two people computing the same thing differently. | — |

URLs (pin these in `tools/fetch_pdfs.py`):

```
Apr 2026  https://www.mospi.gov.in/uploads/publications_reports/publications_reports1779688125413_332125c5-1fb9-4d23-87ca-dd89fc14cd15_Flash_Report_April_2026.pdf
May 2026  https://www.mospi.gov.in/uploads/publications_reports/publications_reports1782388627305_2544b8eb-3ea2-40eb-ab6e-b150c40c4a9e_FlashReport_May_2026.pdf
Jun 2026  https://www.mospi.gov.in/uploads/publications_reports/publications_reports1785229543014_f9b01e19-0a7a-4975-9276-34e02259c2e0_FlashReport_June_2026_.pdf
Jul 2026  https://www.mospi.gov.in/uploads/publications_reports/publications_reports1787656864174_db1695c9-b038-4c20-964f-8cf5f2cdda5f_FlashReport_July_2026_.pdf
Dec 2025  https://www.mospi.gov.in/uploads/publications_reports/publications_reports1769671627281_5812a634-546b-405d-921c-f84c4da453dc_FlashReport_December_2025.pdf
```
(June and July carry a trailing underscore before `.pdf`. May–Jul HEAD-checked by the research agent, not by me; the fetch script must verify size and checksum.)

### 3.2 Parser

| # | Decision | Why | Tag |
|---|---|---|---|
| D6 | **Python 3.12 via `uv venv --python 3.12`**, one `requirements.txt`. | It is what `python` already resolves to; every needed wheel exists; uv pins it per-repo so three laptops match. | verified |
| D7 | **pdfplumber 0.11.x, `lines` strategy, as the primary extractor; PyMuPDF 1.28.x as fallback.** Not pypdf+regex. | Table 6 is a ruled table with multi-line cells; ruling-line geometry is exactly what pdfplumber's `lines` strategy uses, and the 13% regex misses were all multi-line cells. PyMuPDF is 3–5× faster if tuning stalls. | from research |
| D8 | **One adapter per snapshot** (`parser/adapters/2026_04.py` …) feeding one `normalize()` that emits canonical rows plus `parse_flags`. | Dec 2025 lacks PMGID/legacy code; later months may drift again. Never widen the schema for one month. | verified (drift) |
| D9 | **Parse-coverage gate: ≥ 95% of the printed row count per snapshot, and column sums within 0.5% of the page-3 aggregates.** Coverage is displayed on the dashboard and on the model card. | Sum-to-aggregate is a self-check the sponsor's own PDF provides; an unparsed row cannot create a false positive, so showing coverage is honest and cheap. | from research |
| D10 | **Render page images (PNG) for pages that contain a flagged project** via PyMuPDF `get_pixmap()`. | The strongest demo moment is the actual PDF row on screen next to our number. ~100 pages, no network. | assumed (count) |

### 3.3 Findings, models and "backend"

| # | Decision | Why | Tag |
|---|---|---|---|
| D11 | **No server. No API. No FastAPI before 12 Sept.** Findings and models run at build time and write JSON into `web/public/data/`; the frontend loads it over a local static server. | Nothing is live; an API is a third process to fail on stage. Models are scored at build time for every project, so the dashboard shows predictions without running Python. The production architecture (PAIMANA API → ingest → store → findings + models → dashboard on NIC) goes on the architecture slide, labelled target. | from research (architect) |
| D12 | **Committed outputs.** `panel.csv`, `projects.json`, `findings.json`, `models.json`, `briefs.json` are committed after every successful run. | The frontend person's agent never needs Python; the demo laptop never needs to run the pipeline or a model. | — |
| D13 | **Models are scikit-learn only: `HistGradientBoostingClassifier` / `Regressor` as the ML method, `LogisticRegression` / `LinearRegression` as the conventional method, `IsolationForest` for anomalies.** No LightGBM, XGBoost or deep learning. | Zero extra wheels, native NaN handling, `class_weight='balanced'`, and the PS asks for the ML-vs-conventional comparison, which needs both in one library. | from research |
| D14 | **Assistant = precomputed templated Q&A (eight questions) + project-code lookup + cached LLM briefs.** Live free-text mode only if `localhost:11434` answers; hidden otherwise. | Covers outcome (h) offline and deterministically; the briefs are genuinely LLM-written but generated once, verified, and cached. Say on stage: "every number the model wrote was checked against the ledger before it was saved." | from research |
| D15 | **Ministry/sector: capture the table's own section-header rows if Table 6 prints them (Parser Day-1 check); else a top-10 exact-string agency rollup.** No NLP mapping to 17/22 before the round. | The mapping is a normalisation job over 1,981 free strings; a rollup that says it is a rollup is honest. The models use whatever this yields as a categorical. | — |
| D31 | **Prediction targets are schedule-revision filings (M1) and next-month physical progress (M2). Cost escalation is a cross-sectional driver analysis (M3), never a forecast.** | 599 DoC changes vs 23 cost changes per four months in the verified join. A classifier on 23 positives is indefensible; an officer would ask for the count and the pitch would die. | claimed (join counts) |
| D32 | **Out-of-time validation only: train on the earlier report pairs, test on the newest pair (Jun→Jul 2026).** No random train/test splits anywhere. | The PS says "before such issues materialise"; the only honest test is the report the model had not seen. It is also the line the officer cannot argue with. | — |
| D33 | **Every model number on any screen or slide is shown beside its conventional baseline, and the positives count and sample size are printed next to it.** The loser is still shown. | Dimension (b) asks whether ML beats conventional methods; showing both even when the baseline wins is the answer, and it is the thing rival decks will not do. | — |
| D34 | **Two feature sets: A = fields the public CUF-derived table shows; B = A plus audit-derived features (velocity, unreachable ratio, contradiction flags, prior-revision count, agency prior slip rate).** Report A vs B lift. | This is the closest honest answer to dimension (c): how much predictive power comes from the current fields versus variables not captured on the form. We say the CUF itself is behind login. | — |
| D35 | **Explanations: permutation importance (global), SHAP `TreeExplainer` per project (top five factors), logistic coefficients for the baseline.** | Verified supported for HistGradientBoosting; per-project factors feed the project page and the briefs; coefficients make the conventional model fully transparent. | from research |
| D36 | **Determinism: `random_state=0` everywhere, `OMP_NUM_THREADS=1` set at the top of `findings/run.py`, and the validator's double-run diff covers `models.json`.** | scikit-learn does not document thread-level reproducibility for histogram boosting; single-threading costs seconds on 30k rows and removes the doubt. | from research (absence) |
| D37 | **Metrics: PR-AUC, ROC-AUC, precision@100, recall@100, lift@100, calibration bins, plus a label-shuffle control run.** No "accuracy". | Base rates are low; accuracy would be 90% for predicting nothing. Top-100 is the officer's actual decision: which hundred projects to review this month. The shuffle run proves the pipeline is not leaking. | — |
| D38 | **A model card screen and `model_card.json`, generated by the pipeline, listing data, splits, counts, metrics, feature sets, limitations and the fields we cannot see.** | Outcome (i) documentation; also the honesty device that converts "we cannot see the CUF" from a weakness into a stated scope. | — |
| D39 | **LLM: Ollama with `qwen2.5:3b`, `seed=0`, `temperature=0`, briefs generated at build time on P's laptop for the top-60 risk projects plus the demo-path projects; every number in each brief must exist in its fact sheet or the brief is regenerated, then replaced by a template.** Cached in `briefs.json` with `grounded` and `model` fields. | Genuine LLM use that cannot hallucinate on stage because it never runs on stage; the grounding check is a feature judges have not seen. 3B model needs about 8 GB RAM on one laptop only. | from research |
| D40 | **Model outputs are additive: separate `models.json` / `briefs.json` files and a nullable `ml` block per project.** The audit screens never read them. | If any model is cut or fails, the audit layer and the demo path still work unchanged. | — |
| D41 | **Cut order if behind schedule:** 1 live LLM mode → 2 LLM briefs → 3 M4 → 4 M3 partial-dependence charts (keep the benchmark) → 5 F6 → 6 M2 → never cut F1, F2, M1 or the comparison table. | Decided now so nobody decides it at 2 a.m. on the 11th. | — |
| D42 | **The rule-based risk score (F4) stays separate from the model probability; both columns are shown, never blended.** | A blended score is explainable to nobody; two columns let the officer see when rules and model disagree, which is itself a finding. | — |
| D43 | **Monthly Review Pack: one button exports the current watchlist (flags, risk band, slip probability, expected delay, page citations) as CSV.** | Names the manual workflow replaced: IPMD's monthly review list. Costs an hour. | — |

### 3.4 Frontend

| # | Decision | Why | Tag |
|---|---|---|---|
| D16 | **Vite 8 + React + TypeScript, Tailwind v4 (`@tailwindcss/vite`), shadcn/ui components** (table, card, tabs, sheet, badge, command). | The SIH-winner norm; shadcn ships source you own, so no runtime CDN; Tailwind v4 is one import, no config. | from research |
| D17 | **Apache ECharts 6 (`echarts-for-react`) for every chart**, including the India choropleth via `registerMap`, the PR/calibration curves and partial-dependence lines. Not Recharts. | Recharts has no map and lags on 2,000-point scatters (issue #2862); ECharts is canvas and has geo built in. One chart library, one mental model for the agent. | from research |
| D18 | **India states GeoJSON from DataMeet (CC BY 4.0), bundled in `web/src/assets/`.** Verify Ladakh/J&K on Day 1. `react-simple-maps` rejected (unmaintained 4 years). | Post-2019 boundaries matter in a government room; the file must ship offline. | from research (file path unverified) |
| D19 | **TanStack Table + TanStack Virtual for the 2,000-row tables.** | Sorting/filtering/virtualisation without hand-rolling; 2k rows in plain DOM stutter. | from research |
| D20 | **Zod schemas generated from the JSON Schema files** (`json-schema-to-zod`) and applied at load. The app refuses to render on a contract violation and prints which key failed. | The same schema file validates Python output and TypeScript input; the frontend agent cannot silently "fix" a mismatch by guessing. | from research |
| D21 | **Light theme only.** | Projectors wash out dark UIs; one theme halves the surface the agent can get wrong. | assumed |
| D22 | **IBM Plex Sans (UI) + IBM Plex Mono (codes, numbers) via `@fontsource`, bundled.** | Designed for dense enterprise data, tabular numerals, not the default AI-generated look, works offline. | — |
| D23 | **Hash routing (`#/project/705526`)** so the operator can deep-link mid-demo. | The demo path is rehearsed; a URL per state means no clicking hunt on stage. | — |
| D24 | **Indian number formatting everywhere** (`Intl.NumberFormat('en-IN')`, "₹ 53,629.73 cr"). | The room reads lakh/crore; a Western grouping reads as foreign. | — |
| D25 | **Run command: `RUN_DEMO.bat` → `python -m http.server 8080 -d web/dist` + open browser.** Fallback laptop with the same clone. | `fetch()` is blocked on `file://`; Python is verified present. Optional Day-6 hardening: `vite-plugin-singlefile` for a double-clickable HTML (unverified). | from research |

### 3.5 Team and repo

| # | Decision | Why | Tag |
|---|---|---|---|
| D26 | **One private GitHub repo `agrim`, cloned to `C:\dev\agrim` (outside OneDrive).** | Three repos with three agents reproduces the last failure (three private definitions of the panel). OneDrive + node_modules + git = file locks and sync churn. | — |
| D27 | **Directory-exclusive ownership.** `parser/` + `findings/models/m3_drivers.py` + `findings/briefs.py` P; `findings/` (rest) A; `web/` + `deck/` S; `contracts/` + `tools/` lead only. | Zero merge conflicts by construction; an agent that edits outside its directory is caught at review. P takes M3 and the briefs because both need only one snapshot or the finished outputs, and P's parser finishes on Day 3. | — |
| D28 | **Long-lived branches `p/parser`, `p/findings`, `p/surface`; merge `main` into your branch every morning; PR to `main` only when `python tools/validate.py` exits 0.** No rebasing. | AI agents + rebase + students is a conflict factory. The validator, not a person, is the arbiter. | — |
| D29 | **Contract freeze at end of Day 3**, including `models.schema.json` and the `ml` block. After that, only additive nullable fields (minor bump). | Every day of open schema is a day the three outputs can drift apart. | — |
| D30 | **Tool-to-component mapping: Claude Code → Parser (P); ChatGPT → Findings and models (A); Cursor → Surface (S).** Swapping is allowed; the contracts do not care. | The parser needs a terminal, PDFs and long deterministic runs; the findings are single-file numerical modules driven by an exact spec, which is what a chat tool with a code sandbox does well; the dashboard is many-file UI iteration in an IDE. Details in §11.6. | from research (tool capabilities) |

---

## 4. Repository layout

```
agrim/
  AGENTS.md                  <- every agent reads this first (content in §11.2)
  CLAUDE.md                  <- one line: "@AGENTS.md"
  .cursor/rules/agrim.mdc    <- AGENTS.md text + "you may edit only web/ and deck/", alwaysApply: true
  README.md                  <- how to run the demo in 3 commands
  RUN_DEMO.bat
  requirements.txt           <- pdfplumber, pymupdf, pandas, scikit-learn, shap, jsonschema, ollama, pytest (pinned)
  .python-version            <- 3.12
  contracts/
    panel.schema.json        <- one panel row
    projects.schema.json     <- one project object, incl. the nullable ml block
    findings.schema.json     <- the findings envelope
    models.schema.json       <- the models envelope (metrics, importances, curves, counts)
    briefs.schema.json       <- one cached brief
    enums.json               <- closed vocabularies
    CHANGELOG.md             <- one dated line per change
    fixtures/
      panel.sample.csv       <- 12 projects x 5 snapshots, hand-written, every layout variant and event class
      projects.sample.json   <- golden output for the fixture (ml blocks null)
      findings.sample.json   <- golden output for the fixture
      synthetic_panel.py     <- generates a 600-project x 5-snapshot synthetic panel (seed 0) for model tests
  tools/
    fetch_pdfs.py            <- pinned URLs + checksums -> data/pdfs/
    validate.py              <- THE gate (behaviour in §6.6)
    context_pack.py          <- builds CONTEXT_<component>.md for tools that cannot read the repo (§11.6)
  data/
    pdfs/                    <- committed PDFs + SHA256SUMS
    out/panel.csv            <- committed parser output
    out/parse_coverage.md    <- per-snapshot coverage + characterised misses
    pages/<snapshot>/p<page>.png  <- rendered pages for flagged projects
  parser/                    <- P
    adapters/2025_12.py 2026_04.py 2026_05.py 2026_06.py 2026_07.py
    normalize.py  run.py  tests/
  findings/                  <- A (except the two files marked P)
    contradictions.py exits.py early_warning.py risk.py field_audit.py disclosure_lag.py assistant.py
    features.py              <- the one feature builder every model uses (§7B.0)
    models/
      m1_slip.py  m2_progress.py  m3_drivers.py (P)  m4_anomaly.py  metrics.py  model_card.py
    briefs.py (P)            <- Ollama briefs + grounding check
    run.py  tests/
  web/                       <- S
    public/data/projects.json findings.json models.json briefs.json model_card.json  <- committed outputs
    src/ ...
  deck/                      <- S
    numbers.json             <- every number on a slide, generated by findings/run.py
    AGRIM-SIH26103.pptx  AGRIM-SIH26103.pdf
    pitch.md
```

---

## 5. The three components

Each has exactly one input, one output, an owner, and a definition of done that a script can check.

### 5.1 Parser, drivers model, briefs — owner P (Claude Code)

- **Consumes:** `data/pdfs/*.pdf` + `SHA256SUMS`; for M3 and briefs, the committed `panel.csv` / `projects.json`.
- **Produces:** `data/out/panel.csv` (schema §6.1), `data/out/parse_coverage.md`, `data/pages/**.png`; `findings/models/m3_drivers.py` output inside `models.json` (via A's `run.py` hook); `web/public/data/briefs.json`.
- **Done when:** `validate.py` passes; every snapshot's parsed row count ≥ 95% of the printed count; Original/Revised/Expenditure column sums within 0.5% of the page-3 aggregates for that report; each miss class is named in `parse_coverage.md` with a count; M3 produces the benchmark residual for every project in the latest snapshot; `briefs.json` has a brief for every project in the demo path with `grounded: true`.
- **Day-1 checks P must report in the group chat:** (a) does Table 6 carry section-header rows naming ministry/sector? (b) does the PDF print a "projects commissioned during the month" list, or only a count? (c) exact page range of Table 6 in each of the five PDFs; (d) whether project 705526's ₹53,629.73 cr → ₹401.84 cr has a footnote or re-scoping note in either PDF.
- **Tests:** a fixture-page test per adapter; the aggregate-sum test; a determinism test (two runs, identical CSV bytes); an M3 smoke test on the synthetic panel; a briefs grounding test with a deliberately wrong number that must be rejected.

### 5.2 Findings and prediction models — owner A (ChatGPT)

- **Consumes:** `data/out/panel.csv` only.
- **Produces:** `web/public/data/projects.json`, `findings.json`, `models.json`, `model_card.json`, `deck/numbers.json`.
- **Done when:** `validate.py` passes (schemas, enums, determinism: two runs byte-identical including `models.json`); every number that appears on a slide exists in `deck/numbers.json`; the fixture CSV reproduces `findings.sample.json` exactly; `pytest findings/tests` passes on the synthetic panel; M1's shuffle-control PR-AUC is within 0.02 of the base rate; every metric in `models.json` carries `n`, `positives` and `test_pair`.
- **Rule:** every finding row and every model score carries `sources` = `{snapshot, page}` for the rows it was computed from. No number without a page.

### 5.3 Surface — owner S (Cursor): dashboard, deck, pitch

- **Consumes:** `web/public/data/*.json` (through the generated Zod schemas) and `deck/numbers.json`.
- **Produces:** `web/dist/` (built app), `deck/*.pdf`, `deck/pitch.md`.
- **Done when:** the app renders the fixture JSON on Day 1 and the real JSON on Day 4 with zero console errors; every screen in §8 exists; the Predictions screen shows the comparison table with positives counts; no numeric literal of three or more digits appears in `web/src` or in slide text (validator grep); the deck is the unaltered template, six slides, exported to PDF; the pitch has been timed under 3:00 three times.

---

## 6. Contracts

### 6.1 `panel.csv` — one row per (snapshot, project)

| column | type | null | meaning |
|---|---|---|---|
| `snapshot` | `YYYY-MM` | no | report month |
| `source_file` | string | no | file name in `data/pdfs/` |
| `source_sha256` | string | no | checksum of that file |
| `page` | int | no | PDF page the row was read from |
| `sl_no` | int | no | printed serial; **PK = (snapshot, sl_no)** |
| `project_code` | string, 6 digits | yes | primary join key across snapshots |
| `legacy_ocms_code` | string | yes | OCMS-era key; absent in Dec 2025 |
| `pmgid` | string | yes | absent in Dec 2025 |
| `project_name` | string | no | verbatim, whitespace-collapsed |
| `agency_raw` | string | yes | verbatim parenthetical |
| `table_section` | string | yes | nearest section-header row above, if Table 6 prints them |
| `state` | string | yes | verbatim, multi-line joined with a space |
| `approval_month` | `YYYY-MM` | yes | "Date of Approval" |
| `start_month` | `YYYY-MM` | yes | "(Start Date)" |
| `doc_original` | `YYYY-MM` | yes | Original/Target DoC |
| `doc_revised` | `YYYY-MM` | yes | (Revised DoC) |
| `cost_original_cr` | number | yes | ₹ crore, commas stripped |
| `cost_revised_cr` | number | yes | |
| `expenditure_cum_cr` | number | yes | |
| `physical_progress_pct` | number 0–100 | yes | |
| `parse_flags` | string | no | `;`-joined codes from `enums.json`; `""` when clean |

Rules: empty cell = NULL = "not printed". Never 0, never "NA". Numbers are plain decimals. No derived columns.

### 6.2 `projects.json` — array of

```
{ project_code, project_name, agency_raw, state, sector (nullable),
  status: "ongoing" | "exited", first_seen, last_seen,
  snapshots: [ { snapshot, page, doc_original, doc_revised,
                 cost_original_cr, cost_revised_cr, expenditure_cum_cr,
                 physical_progress_pct } ],            // ascending by snapshot
  flags: [ { type, severity, from_snapshot, to_snapshot,
             before, after, detail, sources: [{snapshot, page}] } ],
  risk: { score: 0..100, band: "red"|"amber"|"green", reasons: [string] },
  ml: null | {                                           // additive; null when models are cut
      slip_prob, slip_rank, slip_top_factors: [ { feature, contribution, value } ],
      progress_next_pred, expected_completion (YYYY-MM | null), expected_delay_months (nullable),
      peer_expected_cost_overrun_pct, cost_overrun_residual_pct,
      peer_expected_time_overrun_months, time_overrun_residual_months,
      anomaly_score, anomaly_flag: bool,
      scored_at_snapshot } }
```

### 6.3 `findings.json` — envelope

```
{ meta: { contract_version, generated_at, snapshots: [...],
          coverage: [ { snapshot, rows_parsed, rows_printed, pct } ],
          headline: { projects_latest, cost_revised_total_cr, overrun_total_cr,
                      contradictions_total, exits_total, unreachable_total } },
  contradictions: { by_type: [ { type, count } ],
                    rows: [ { project_code, project_name, type, severity,
                              from_snapshot, to_snapshot, before, after,
                              sources: [...] } ] },
  exits:  { pairs: [ { from, to, exited, entered, exited_cost_revised_cr,
                       commissioned_printed (nullable) } ],
            rows:  [ { project_code, project_name, last_seen, last_progress_pct,
                       last_expenditure_cr, last_cost_revised_cr, partition } ] },
  early_warning: { rows: [ { project_code, velocity_pct_per_month, months_needed,
                             months_remaining, ratio, severity, sources } ] },
  field_audit: { terminal_digit: [ { digit, count, share } ],
                 whole_number_share, multiple_of_5_share, multiple_of_10_share,
                 staleness_by_agency: [ { agency_raw, projects, share_unchanged } ] },
  disclosure_lag: { status: "computed" | "not_computed", rows: [...] },
  by_state:  [ { state, projects, flagged, red } ],
  by_sector: [ { sector, projects, flagged, red } ],
  review_pack: [ { project_code, ...columns of the CSV export } ],
  assistant: [ { id, question, answer, sources: [...] } ] }
```

### 6.4 `models.json` — envelope

```
{ meta: { contract_version, generated_at, sklearn_version, random_state, omp_threads,
          pairs: [ { id, from, to, gap_months, n, positives, censored_exits } ],
          test_pair, train_pairs: [...] },
  m1_slip: {
     feature_sets: { A: [names], B: [names] },
     results: [ { model_id: "LR_A"|"HGB_A"|"HGB_B"|"HGB_B_SHUFFLED", test_pair,
                  n, positives, base_rate, pr_auc, roc_auc,
                  precision_at_100, recall_at_100, lift_at_100,
                  calibration: [ { bin, mean_pred, mean_obs, n } ],
                  pr_curve: [ { recall, precision } ] } ],
     importance_HGB_B: [ { feature, mean, std } ],
     coefficients_LR_A: [ { feature, coef } ],
     watchlist: [ { project_code, slip_prob, slip_rank } ] },     // scored at the latest snapshot
  m2_progress: {
     results: [ { model_id: "ZERO"|"OWN_VELOCITY"|"HGB", test_pair, n, mae, median_ae } ],
     winner: model_id,
     agreement_with_F3: { n, share_same_direction } },
  m3_drivers: {
     snapshot, n,
     results: [ { target: "cost_overrun_pct"|"time_overrun_months",
                  model_id: "OLS"|"HGB", cv_r2, cv_mae } ],
     partial_dependence: [ { target, feature, grid: [x], values: [y] } ],
     sector_effects: [ { sector, effect_cost_pct, effect_time_months, n } ],
     coefficients_OLS: [ { target, feature, coef } ] },
  m4_anomaly: { n, contamination, flagged: [ { project_code, pair, score, sources } ] } }
```

### 6.5 `briefs.json`, `enums.json`

`briefs.json`: array of `{ project_code, brief, model, seed, generated_at, grounded: bool, attempts, facts_hash }`.

`enums.json`:
- `finding_type`: `EXP_DECREASE`, `PROG_DECREASE`, `EXP_GT_REVISED_COST`, `ZERO_PROG_NONZERO_EXP`, `PROG_GT_100`, `DOC_BEFORE_APPROVAL`, `DOC_PASSED`, `DOC_UNREACHABLE`, `DOC_REVISED_FILED`, `COST_REVISED_FILED`, `STAT_ANOMALY`
- `severity`: `critical`, `high`, `medium`, `low`, `info`
- `exit_partition`: `LAST_SEEN_GE_95`, `LAST_SEEN_50_95`, `LAST_SEEN_LT_50`, `UNKNOWN`
- `parse_flag`: `MULTILINE_STATE`, `NO_PMGID`, `NO_LEGACY_CODE`, `NO_PROJECT_CODE`, `NUM_PARSE_FAIL`, `DATE_PARSE_FAIL`, `ROW_SPANS_PAGE`
- `model_id`: `LR_A`, `HGB_A`, `HGB_B`, `HGB_B_SHUFFLED`, `ZERO`, `OWN_VELOCITY`, `HGB`, `OLS`
- `pair_id`: `P1` (2025-12→2026-04), `P2` (04→05), `P3` (05→06), `P4` (06→07)
- `snapshot`: the five allowed values.

### 6.6 `tools/validate.py` — what the gate does

1. Validates every `panel.csv` row against `panel.schema.json`; every `projects.json` element and `findings.json`, `models.json`, `briefs.json` against theirs; `additionalProperties: false` everywhere.
2. Checks every enum-typed value against `enums.json`.
3. Runs `findings/run.py --no-models` twice on `contracts/fixtures/panel.sample.csv` and diffs the outputs (determinism of the audit layer).
4. Asserts the fixture run equals `findings.sample.json` and `projects.sample.json` byte-for-byte.
5. Runs `pytest findings/tests -q` (model tests on the synthetic panel: shapes, determinism across two fits, shuffle control near base rate, no feature from the target pair leaks into features — a test asserts that changing t1 values does not change any t0 feature).
6. Greps `web/src/**` and `deck/pitch.md` for any literal of three or more digits that is not inside `web/public/data/` (hardcoded-number trap); whitelists years and pixel sizes by pattern.
7. Checks every entry in `deck/numbers.json` exists somewhere in `findings.json` or `models.json`.
8. Exit 0 or 1, one line per failure.

**Versioning:** `contract_version` in every JSON file. Additive + nullable = minor bump, no coordination. Rename/retype/remove/nullability change = major bump, lead's sign-off in chat, both fixtures updated in the same commit. **No major bump after Day 3.**

---

## 7. Findings — exact arithmetic (so any model produces the same output)

Let `months(a, b)` = whole months from snapshot `a` to `b`. All comparisons are on the same `project_code`; rows without a code are excluded from cross-snapshot findings and counted in `meta.coverage`.

**F1 Contradiction Ledger** — for each consecutive pair (Dec 2025→Apr 2026, Apr→May, May→Jun, Jun→Jul):

| type | condition | severity |
|---|---|---|
| `EXP_DECREASE` | `exp[t1] < exp[t0]` by more than ₹0.01 cr | critical if drop ≥ 10% of `exp[t0]` else high |
| `PROG_DECREASE` | `prog[t1] < prog[t0]` by more than 0.01 pt | high if drop ≥ 5 pt else medium |
| `EXP_GT_REVISED_COST` | `exp[t] > cost_revised[t]` (single snapshot) | medium (the ministry itself used to annex this class; do not lead with it) |
| `ZERO_PROG_NONZERO_EXP` | `prog[t] == 0 and exp[t] > 0` | low |
| `PROG_GT_100` | `prog[t] > 100` | medium |
| `DOC_BEFORE_APPROVAL` | `doc_original < approval_month` | low |
| `DOC_REVISED_FILED` / `COST_REVISED_FILED` | `doc_revised` / `cost_revised_cr` differs between t0 and t1 | info (events, not errors; they feed F4, F6 and M1's label) |
| `STAT_ANOMALY` | from M4, top 2% anomaly score in a pair | info |

Lead the pitch with `EXP_DECREASE` and `PROG_DECREASE`: a cumulative field cannot fall.

**F2 Exit Ledger** — for each consecutive pair: `exited` = codes in t0 not in t1; `entered` = codes in t1 not in t0. For each exit record the last observed row and `partition` by last progress: ≥95 → `LAST_SEEN_GE_95`; 50–95 → `LAST_SEEN_50_95`; <50 → `LAST_SEEN_LT_50`; NULL → `UNKNOWN`. Store `commissioned_printed` if the parser captured the report's own count. **Wording rule:** "left the monitored panel", never "cancelled".

**F3 Unreachable DoC** — for each project with ≥ 2 snapshots and `prog[latest] < 100`:
- `velocity` = OLS slope of `physical_progress_pct` on months, over all available snapshots (min 2).
- `doc_current` = `doc_revised[latest]` if present else `doc_original[latest]`.
- `months_remaining` = `months(latest, doc_current)`.
- If `months_remaining ≤ 0` → flag `DOC_PASSED` (a fact, not a forecast), severity high.
- Else if `velocity ≤ 0` → `DOC_UNREACHABLE`, severity critical, `months_needed = null`, detail "no reported progress over N months".
- Else `months_needed = (100 − prog[latest]) / velocity`; `ratio = months_needed / months_remaining`; flag if `ratio > 1`: critical ≥ 2.0, high 1.25–2.0, medium 1.0–1.25.
- Sentence template: "At its own reported pace ({velocity} pt/month), this project needs {months_needed} months; its own stated date leaves {months_remaining}."

**F4 Rule-based risk score** (v1 weights, chosen for legibility, not fitted — say so on the slide):
`DOC_UNREACHABLE` critical +40 / high +25 / medium +10; `DOC_PASSED` +25; `EXP_DECREASE` +20; `PROG_DECREASE` +15; `EXP_GT_REVISED_COST` +10; `ZERO_PROG_NONZERO_EXP` +5; `DOC_REVISED_FILED` +10; `COST_REVISED_FILED` +5. Cap 100. Band: ≥60 red, 30–59 amber, else green. `reasons` = the human sentence for each contributing flag. M1's probability is displayed beside it, never added to it (D42).

**F5 Field-Information Audit** — on the latest snapshot: distribution of the last digit of `floor(physical_progress_pct)`; share of values that are whole numbers, multiples of 5, multiples of 10 (expected under a continuous measure ≈ 1%, 20%, 10% of whole numbers). Staleness: per `agency_raw` with ≥ 5 projects, share of projects whose `expenditure_cum_cr` is unchanged across every consecutive pair.

**F6 Disclosure Lag** (stretch) — for each project with `DOC_REVISED_FILED` between t_k and t_{k+1}: for j ≤ k, recompute F3 using only snapshots ≤ t_j and the DoC stated at t_j; `first_unreachable` = smallest such t_j flagged; `lag_months = months(first_unreachable, t_{k+1})`. Report the distribution and the median; if the median is 0, say so (the honest null result).

**Assistant** — eight fixed questions rendered from the envelope, each answer a template with numbers substituted and a `sources` list:
1. Which projects report cumulative expenditure falling between {t0} and {t1}?
2. Which projects cannot reach their stated completion date at their own reported pace?
3. What left the monitored panel between {t0} and {t1}, and in what state?
4. Which state has the most flagged projects?
5. How reliable is the Physical Progress field as filled?
6. What share of the source reports did AGRIM parse?
7. Why is project {code} rated {band}, and what does the model say? (bound to the current project; reads `risk.reasons` and `ml.slip_top_factors`)
8. Did the model beat the conventional method on the July report? (reads `models.json`)
Plus one free input: a project-code search box that opens the project page.

---

## 7B. Models — exact specification (so any model produces the same output)

### 7B.0 Feature builder — `findings/features.py` (one function, used by every model)

`build_pair_features(panel, t0, t1)` returns one row per `project_code` present in **both** t0 and t1 (projects that exit are excluded and counted as `censored_exits`), with all features computed from snapshots **≤ t0 only**. `build_snapshot_features(panel, t)` returns the same feature columns for every project present at `t` (used to score the latest month and for M3). A unit test asserts that changing any value at t1 leaves every feature unchanged (leakage guard).

**Set A — fields visible in the public table (CUF-derived):**
`physical_progress_pct`, `exp_share` = `exp / cost_revised` (NaN if cost null or 0), `age_months` = `months(approval_month, t0)`, `months_to_doc` = `months(t0, doc_current)`, `log_cost_original` = `ln(cost_original + 1)`, `cost_overrun_pct` = `(cost_revised − cost_original) / cost_original × 100`, `time_overrun_months` = `months(doc_original, doc_revised)` (0 if no revised), `has_revised_doc` (0/1), `sector` (categorical from `table_section` or the agency rollup; "UNKNOWN" if null), `state` (categorical), `gap_months` = `months(t0, t1)` (known at t0: the next report is monthly except across the Dec→Apr gap).

**Set B — Set A plus audit-derived and history features (not on the form):**
`velocity_pct_per_month` (OLS slope over snapshots ≤ t0; NaN if fewer than 2), `unreachable_ratio` (F3 ratio at t0; NaN if not computable), `n_prior_revisions` (count of earlier pairs where `doc_revised` changed; NaN for the first pair), `agency_prior_slip_rate` (share of the agency's projects with a DoC change in pairs strictly before t0; NaN for the first pair), `n_flags_to_t0` (count of F1 flags with `to_snapshot ≤ t0`), `exp_decrease_ever` (0/1).

NaN is passed through unchanged to HistGradientBoosting (native support). For logistic/linear models only, NaN is median-imputed inside the pipeline (`SimpleImputer`), categoricals one-hot encoded with `handle_unknown='ignore'`, numerics standardised.

### 7B.1 M1 — Slip-filing classifier (`m1_slip.py`)

- **Pairs:** P1 Dec 2025→Apr 2026, P2 Apr→May, P3 May→Jun, P4 Jun→Jul.
- **Label:** `y = 1` if `doc_revised[t1] != doc_revised[t0]` (including NULL → value). Everything else 0.
- **Split:** train on P1+P2+P3, test on P4. Secondary check: train on P1+P2, test on P3 (reported as a second row so the panel can see stability).
- **Models:** `LR_A` = logistic regression on Set A (`class_weight='balanced'`, `max_iter=1000`); `HGB_A` = `HistGradientBoostingClassifier` on Set A; `HGB_B` = the same on Set B. HGB params: `max_iter=300`, `learning_rate=0.05`, `early_stopping=True`, `validation_fraction=0.15`, `class_weight='balanced'`, `categorical_features='from_dtype'`, `random_state=0`. `HGB_B_SHUFFLED` = HGB_B fitted on labels permuted with seed 0 (control).
- **Metrics on the test pair:** `n`, `positives`, `base_rate`, `pr_auc` (`average_precision_score`), `roc_auc`, `precision_at_100` (mean label of the 100 highest scores), `recall_at_100` (share of all positives inside that 100), `lift_at_100 = precision_at_100 / base_rate`, 10-bin calibration, PR curve points.
- **Explanations:** `permutation_importance` on the test pair for HGB_B (`n_repeats=10`, `scoring='average_precision'`, `random_state=0`); SHAP `TreeExplainer(HGB_B)` on the latest-snapshot features → top five `{feature, contribution, value}` per project into `ml.slip_top_factors`; LR_A coefficients table.
- **Scoring for the dashboard:** refit HGB_B on P1–P4, score every ongoing project at Jul 2026 → `ml.slip_prob`, `ml.slip_rank`; the top 100 is the **watchlist**.
- **Reporting rule:** the sentence template for slides and the assistant is: "On the July report, which the model never saw, {HGB_B recall_at_100 as count} of the {positives} projects that filed a revised date were in the model's top 100; logistic regression found {LR_A count}; audit-derived features added {lift difference} of that." If LR_A wins, the sentence says so.

### 7B.2 M2 — Progress forecaster (`m2_progress.py`)

- **Pairs and split:** train on P2+P3 (one-month pairs), test on P4. P1 is excluded from training because its 4-month gap is not a "next month" (say so on the model card).
- **Target:** `delta = prog[t1] − prog[t0]` (points per month). Rows with `PROG_DECREASE` are kept; the model card reports MAE with and without them.
- **Methods:** `ZERO` (predict `delta = 0`); `OWN_VELOCITY` (the project's own OLS slope over snapshots ≤ t0; if fewer than 2 snapshots, the sector median delta from the training pairs); `HGB` = `HistGradientBoostingRegressor(loss='absolute_error', max_iter=300, learning_rate=0.05, early_stopping=True, random_state=0)` on Set B.
- **Metric:** MAE and median absolute error of `prog[t1]` on P4 for the three methods; `winner` = lowest MAE.
- **Derived outlook per ongoing project at Jul:** simulate monthly increments with the winner (increment refreshed each simulated month from the model with updated progress; capped at 120 months) until 100 → `ml.expected_completion`; `ml.expected_delay_months = months(doc_current, expected_completion)` (negative = ahead). Store `ml.progress_next_pred`.
- **Cross-check:** `agreement_with_F3` = share of projects where the sign of `expected_delay_months` matches F3's flag.

### 7B.3 M3 — Overrun drivers and peer benchmark (`m3_drivers.py`, owner P)

- **Snapshot:** the latest (Jul 2026). Universe: `cost_original > 0` and `approval_month` present.
- **Targets:** `cost_overrun_pct` clipped to [−50, 500]; `time_overrun_months` (0 if no revised DoC) clipped to [0, 240].
- **Features:** `log_cost_original`, `age_months`, `physical_progress_pct`, `approval_year`, `agency_size` (projects of the agency in the snapshot), `sector`, `state`.
- **Models:** `OLS` (`LinearRegression` in a one-hot + scaler pipeline) and `HGB` (`HistGradientBoostingRegressor(random_state=0)`), each evaluated with `KFold(5, shuffle=True, random_state=0)` → `cv_r2`, `cv_mae`.
- **Drivers:** `sklearn.inspection.partial_dependence` (grid 20) for `log_cost_original`, `age_months`, `physical_progress_pct` on the HGB; `sector_effects` = OLS sector coefficients relative to the largest sector.
- **Benchmark:** `cross_val_predict` (HGB) → `ml.peer_expected_cost_overrun_pct` and `ml.peer_expected_time_overrun_months`; residuals = actual − expected → "worse than comparable projects by {x} points / {y} months".

### 7B.4 M4 — Statistical anomaly detector (`m4_anomaly.py`)

- **Rows:** every (project, pair) with both snapshots present. Features: `Δexp`, `Δexp / cost_revised`, `Δprog`, `Δcost_revised`, `gap_months`, `physical_progress_pct[t0]`.
- **Model:** `IsolationForest(contamination='auto', random_state=0)`; `anomaly_score = −score_samples`; flag the top 2% per pair as `STAT_ANOMALY` (severity info). Arithmetic impossibilities from F1 stay separate and are never re-labelled by M4.

### 7B.5 LLM briefs (`briefs.py`, owner P)

- **Universe:** top 60 projects by F4 score plus every project on the demo path (§8), deduplicated.
- **Fact sheet per project:** name, agency, state, codes; each snapshot's numbers; every flag sentence; `risk.reasons`; `ml` numbers with plain-language labels; the page citations.
- **Model:** Ollama `qwen2.5:3b`, `options={"seed": 0, "temperature": 0, "num_ctx": 4096}`. System prompt: "You write a four-sentence brief for a monitoring officer. Use only the facts below. Do not introduce any number that is not in the facts. Plain English, no headings."
- **Grounding check:** every numeric token in the brief (after removing commas and the ₹ sign) must appear in the fact sheet; otherwise regenerate with the sentence "Your previous answer contained a number not in the facts: {n}. Remove it." Up to two retries; then the template brief with `grounded: false` is stored instead.
- **Cache:** `briefs.json`; the dashboard shows a chip "LLM brief · qwen2.5:3b · verified against ledger". Regenerate only when `facts_hash` changes.
- **Live mode:** the Assistant screen probes `GET http://localhost:11434/`; if the body is "Ollama is running", a free-text box appears and questions are answered by the same model with the current project's fact sheet injected; otherwise the box is hidden. Never used on the rehearsed path.

### 7B.6 Model card (`model_card.py` → `model_card.json`)

Sections, all generated from `models.json` and `findings.json`: data (five reports, coverage per report), universe and censoring (exits excluded from labels, counts), targets and why cost escalation is not a target (positives count), feature sets A and B with the note that the CUF itself is behind login, splits, results table with baselines, shuffle control, calibration, known limitations (labels are reporting events; the panel is survivor-selected; nine public fields), what would change with PAIMANA access, versions and seeds.

---

## 8. The judge-facing UX

**Design tokens** (S implements once, in `web/src/index.css`):

| token | value | use |
|---|---|---|
| ground | `#F4F6F8` | page background |
| surface | `#FFFFFF` | cards, table |
| ink | `#0E1A2B` | primary text |
| ink-muted | `#4B5A6B` | secondary text, labels |
| line | `#D5DCE4` | borders, grid |
| accent | `#1F5FA8` | links, selected state, primary button |
| critical / high / medium / ok | `#B42318` / `#C2410C` / `#B7791F` / `#1E7B4F` | severity only, never decoration |
| model | `#5B4B9A` | anything model-derived (probabilities, forecasts, SHAP bars) so rule-based and model-based are never confused |
| type | IBM Plex Sans 15px base, 1.5 line-height; IBM Plex Mono for codes and every number column with `font-variant-numeric: tabular-nums` | |
| density | 8/12/16/24 px spacing scale; tables at 36 px rows | dashboard density |

**Layout:** left rail in three groups — **Audit** (Overview, Ledger, Exits, Fields), **Outlook** (Early Warning, Predictions, Drivers), **About** (Assistant, Model Card) — a 56 px header carrying the persona switch (IPMD national / Ministry officer, which is a filter), the coverage chip ("5 reports · 9,4xx rows · 97% parsed") and the **Export review pack** button; content area max 1440 px. Every screen: summary strip first, detail below. Severity is encoded twice: a colour chip *and* a word. Model-derived numbers always carry the model colour and the word "model".

**Screens (routes):**

| route | what it shows | the sentence the operator says |
|---|---|---|
| `#/` **Overview** | KPI strip (projects in latest report, revised cost, overrun, contradictions, exits, unreachable-DoC count, watchlist size); India map shaded by flagged count per state; top-20 table with both the rule band and the model probability | "Five public reports, parsed; every number here has a page." |
| `#/ledger` **Contradiction Ledger** | table grouped by type; columns: project, months, before → after, Δ, severity, page; type filter chips (arithmetic types first, `STAT_ANOMALY` last); click row → project | "A cumulative field cannot go down. Here are the 27 that did." |
| `#/project/:code` **Project** | header (name, agency, state, codes); two sparklines (progress, expenditure) across snapshots with DoC markers and the **forecast tail** in model colour; flags list with sentences; rule risk score with reasons; **Outlook card**: slip probability with the five SHAP bars, expected completion vs stated date, peer benchmark line ("worse than comparable projects by X"); **"Source page" button opens the rendered PDF page image**; LLM brief with the verified chip; assistant panel bound to this project | "Their own PDF. ₹53,629 crore in December, ₹402 crore in April, progress up. And the model's view, with the five reasons." |
| `#/exits` **Exit Ledger** | waterfall per pair (Apr→May→Jun→Jul): exited / entered; partition bars; table of exits with last state; caveat line ("net changes; exit reason is behind login") | "Two hundred and six projects left in three months. The report says nine were commissioned in April." |
| `#/warning` **Early Warning** | table sorted by F3 ratio; sentence per row; distribution chart of ratio | "No model. Their own two numbers disagree." |
| `#/predict` **Predictions** | top: the **comparison table** (LR_A / HGB_A / HGB_B / shuffled control × PR-AUC, precision@100, recall@100, lift) with `n` and `positives` printed in the header; PR curve and calibration chart; below: the **watchlist** (top 100 by probability, columns: project, probability, rank, top factor, rule band, expected delay, page) | "We trained on December to June and tested on July, which the model never saw. Gradient boosting versus logistic regression, side by side. The audit features added this much." |
| `#/drivers` **Drivers & Benchmark** | three partial-dependence lines (size, age, progress) per target; sector effect bars; scatter of expected vs actual overrun with the current project highlighted; sector and agency leaderboards | "What drives overrun across the panel, and how each project compares with its peers." |
| `#/fields` **Field Audit** | histogram of terminal digits with the uniform line; staleness by agency | "Which of your fields are measured, and which are guessed." |
| `#/assistant` **Assistant** | question list + answer with source chips; code search; free-text box only when the local model is running | "It answers only from the ledger, with a page for every number." |
| `#/model-card` **Model Card** | the generated card, one column, printable | "Everything we cannot see, stated." |

**Interaction rules:** everything clickable has hover + focus states; tables virtualised; empty states say what would be needed; loading skeletons reserve space; keyboard `/` focuses search. No animation beyond 150–200 ms fades.

**The 95-second demo path** (operator rehearses this exact sequence): `#/` (5 s) → `#/ledger?type=EXP_DECREASE` (15 s) → `#/project/705526` → Source page → Outlook card (30 s) → `#/predict` comparison table then watchlist (25 s) → `#/exits` (15 s) → `#/assistant` question 8 (5 s).

---

## 9. Deck and pitch

**Template rules [from research, template read]:** six slides max including title; headings and pointer text fixed; PDF only; points and diagrams, no paragraphs. Do not restyle. Numbers on slides come from `deck/numbers.json` — S pastes, never types.

| Slide | Heading (verbatim) | Content |
|---|---|---|
| 1 | TITLE PAGE | PS ID SIH26103, title, theme Smart Automation, Software, team ID/name |
| 2 | IDEA TITLE / Proposed Solution | AGRIM in one line; the 705526 fact as the first bullet; audit layer (F1–F5) in three bullets; prediction layer (M1–M3) in three bullets, each with its baseline named; "Innovation and uniqueness": the only entry whose headline is a fact in the sponsor's own PDF, validated out-of-time on the sponsor's next report, with every model shown beside the conventional method |
| 3 | TECHNICAL APPROACH | Architecture flowchart: PAIMANA PDFs/API → pinned fetch → adapter parser → canonical panel → findings engine (F1–F6) → feature builder → models (M1–M4) + LLM briefs with grounding check → static bundle → dashboard; target deployment on NIC; open-source stack named (Python, pdfplumber, scikit-learn, SHAP, Ollama, React, ECharts) |
| 4 | FEASIBILITY AND VIABILITY | What runs today (coverage %, five reports, counts); the comparison table with `n` and positives; risks named honestly: labels are reporting events; panel censored by exit; CUF not visible; cost positives too few to forecast → what we do about each |
| 5 | IMPACT AND BENEFITS | ₹5.65 lakh crore recorded overrun (Apr 2026); 1,105 of 1,702 delayed (Standing Committee, Aug 2026); ~90 impossibilities per month-pair no one currently flags; the watchlist as the officer's Monday list; the review-pack export |
| 6 | RESEARCH AND REFERENCES | Flash Report URLs; PS text; Ram Singh 2009/2011 (the OLS baseline we replicate); The Wire 29 May 2026; ABC Live; PIB releases; guidelines PDF; scikit-learn and SHAP citations; a primary-research consultation if one happens (item 14.2) |

One national-round caveat from a 2022 winner: polished app screenshots in the national PDF can read as pre-built work. Use the architecture flowchart, the comparison table, one ledger table screenshot, and charts of findings rather than a gallery of UI.

**The 3-minute pitch** (one presenter; operator drives the demo silently):

| time | beat |
|---|---|
| 0:00–0:20 | The fact. "In the Ministry's own April report, project 705526 reports ₹53,629 crore spent. In the next report, ₹402 crore. Progress went up. Nobody flagged it. We found 90 more like it in one pair of months." |
| 0:20–1:35 | Live demo along the path in §8, ending on the Predictions screen. |
| 1:35–2:05 | The model beat, one sentence from §7B.1's template, then: "Same words as every other team — gradient boosting, SHAP, an LLM. Three differences you can check: we tested on the report the model never saw, we show the conventional method even where it wins, and every metric carries its positives count." |
| 2:05–2:30 | Impact: the three numbers from slide 5; the watchlist and the review pack as what the officer uses Monday. |
| 2:30–2:48 | How: five public PDFs, deterministic audit, scikit-learn models, open source, deployable on NIC; the survival model and the 16-month archive as the next step. |
| 2:48–3:00 | Scope limits, said before they are asked: "We audit the record, not the concrete. The CUF is behind login; the model card says what we cannot see." |

If P's Day-1 check finds a footnote explaining 705526, the opener becomes the class: "27 projects whose cumulative expenditure went down."

**Question bank** (rehearse, one owner each): Why this PS? How is this different from an AI dashboard? Isn't a revised DoC just paperwork? (Yes; that is why the label is "will file a revision", the audit layer is separate, and the model card says so.) Where did the 206 projects go? Can it scale nationally / does it need PAIMANA access? What about the CUF question (c)? (Feature set A vs B; the form itself is behind login.) What is your accuracy? (We report PR-AUC and top-100 recall with the positives count; accuracy is meaningless at this base rate.) Why not predict cost overrun? (23 positives per four months.) Why HistGradientBoosting and not LightGBM or a neural network? (Same algorithm family, zero extra dependencies, native NaN handling; the comparison the PS asks for needs the baseline in the same library.) Did you use an LLM? (Yes, offline, for briefs, every number verified against the ledger; live only if the local model is present.)

---

## 10. Seven-day schedule

Today is Saturday 5 Sept. Assumes ~4 focused hours per person per day around classes. Bold rows are gates.

| Day | P — Claude Code | A — ChatGPT | S — Cursor | Checkpoint |
|---|---|---|---|---|
| **0 · Sat 5** (lead, tonight, ~3 h) | Repo, AGENTS.md, CLAUDE.md, `.cursor/rules`, all contract files, fixtures (5 snapshots), `synthetic_panel.py`, `validate.py`, `context_pack.py`, `fetch_pdfs.py` run once, PDFs + checksums committed. Lead reads the 705526 rows in both PDFs. Start the Ollama install and `ollama pull qwen2.5:3b` on P's laptop in the background. | | | Fresh clone → `validate.py` exits 0 |
| **1 · Sun 6** | pdfplumber on April: Table 6 located, row count printed; Day-1 checks (a)–(d) posted | `features.py` on the fixture (both sets, leakage test passing); F1 complete; `run.py` emits valid `projects.json` + `findings.json` | Vite scaffold, tokens, rail, Overview + Ledger on fixture JSON; GeoJSON verified | **#1 end of day: fixture data flows fixture → findings → screen, all three merged to main.** If not, reassign tonight. |
| **2 · Mon 7** | April ≥ 90% rows, sums check; July adapter started; M3 drafted on April alone | F2, F3, F4; M1 code runs end-to-end on the synthetic panel (metrics, shuffle control, SHAP factors) | Project page with sparklines, flags, Outlook card on fixture; assistant panel; Predictions screen skeleton on a fixture `models.json` | |
| **3 · Tue 8** | All five snapshots in one `panel.csv`; coverage report; M3 on the fixture end-to-end | F5; M2, M4; **first real-data run of M1/M2** → metrics posted in chat; `deck/numbers.json` | Exits, Warning, Drivers, Fields, Model Card screens; review-pack export; deck skeleton in template | **Contract freeze** (all five schemas). |
| **4 · Wed 9** | Coverage → 95%; page PNGs for flagged pages; M3 final on July with benchmark residuals | Metric review against the PDF for the top-20 watchlist; shuffle control; SHAP per project; `model_card.json` | Real JSON on every screen; comparison table live | **#2: real data end to end, models included. 705526 on screen with its page image and its Outlook card. Feature work stops until true.** |
| **5 · Thu 10** | Briefs via Ollama (cached, grounded); `parse_coverage.md` final | F6 if time; numbers frozen; deck numbers final | Deck complete, exported to PDF once; pitch written; polish | Cut order D41 applied to anything not green by 22:00 |
| **6 · Fri 11** | Cold-machine rehearsal: second laptop, fresh clone, Wi-Fi off, `RUN_DEMO.bat`, twice. Three timed pitch runs. Bug fixes only. | | | |
| **7 · Sat 12** | Demo. No code changes. USB stick with the repo. | | | |

---

## 11. Stitching protocol (the answer to "three people, three agents")

### 11.1 Why it failed last time and what is different now

Last time the interface between people was prose and memory; each agent invented its own data shape and conventions. This time the interface is five JSON files a script checks, committed fixtures both sides run against, one feature builder every model must use, and a freeze date. A weaker model can still pass a schema validator; the validator, not the strongest agent, defines "correct".

### 11.2 `AGENTS.md` (every agent reads it first; keep under one screen)

- You are working in `agrim/`. You own exactly one directory (named in the prompt). Do not create or edit files outside it, except your own tests.
- `contracts/` is read-only for you. If a field you need does not exist, stop and report; do not add it.
- Inputs and outputs are only the files named in BUILD.md §5 for your component. No other component's code may be imported. Models import features only from `findings/features.py`.
- Empty CSV cell = NULL = "not printed". Never write 0 or "NA" for a missing value.
- Never hardcode a number that comes from the data. Frontend and deck read numbers from JSON.
- Runs must be deterministic: same input, byte-identical output. `random_state=0` on every estimator; `OMP_NUM_THREADS=1`; no timestamps except `meta.generated_at`.
- Model features may use only snapshots at or before the pair's first month. Nothing from the later month is a feature.
- No network access at runtime anywhere. Fetching happens only in `tools/fetch_pdfs.py`; the LLM runs only in `findings/briefs.py` at build time.
- Before you say "done": run `python tools/validate.py` and paste its output. Do not claim tests pass without showing the run.
- New dependency → add it, pinned, to `requirements.txt` or `package.json` in the same commit.
- If a spec line in BUILD.md §7 or §7B is ambiguous, implement the literal reading and leave a `# SPEC?` comment; do not choose a cleverer interpretation.

### 11.3 The prompt preamble each person pastes into every agent session

> Read `AGENTS.md`, then `BUILD.md` sections 5.x, 6, 7 and 7B (x = my component). I own `<dir>/` only. Today's task: `<one line>`. Definition of done: `<copied from §5.x>`. Finish by running `python tools/validate.py` and showing me the output. If you cannot run commands, give me the exact command to run and wait for my pasted output.

### 11.4 Daily rhythm

- Morning: `git merge main` into your branch; 10-minute voice sync: what shipped, what is blocked, any contract question.
- Evening: PR if `validate.py` is green; lead merges; lead posts the checkpoint status.
- Any contract question goes to the group chat, is answered by the lead, and is logged in `contracts/CHANGELOG.md` the same day.

### 11.5 When an agent goes off-script

Symptoms: new fields, a second copy of a function that exists elsewhere (a second feature builder is the classic one), a "helpful" refactor across directories, numbers typed into components, a random train/test split. Response: revert the commit, re-paste the preamble, re-run. Do not negotiate with the agent's version of the schema.

### 11.6 Using this document with three different tools

The repo is the only shared state. Each tool gets the same three things: the rules (`AGENTS.md`), the spec sections for that component, and the fixture. What differs is how each tool receives them and whether it can run the validator itself.

| | Claude Code (P) | Cursor (S) | ChatGPT (A) |
|---|---|---|---|
| Sees the repo? | Yes, reads and edits files, runs commands | Yes, IDE agent with terminal | **No.** It sees only what you paste or upload; the GitHub connector is read-only |
| Reads the rules automatically? | `CLAUDE.md` containing `@AGENTS.md` is loaded every session | `.cursor/rules/agrim.mdc` with `alwaysApply: true`; root `AGENTS.md` also read per docs | No. Put `AGENTS.md`, `CONTEXT_findings.md` and the schemas as **Project files** in a ChatGPT Project so every chat sees them |
| Can run `validate.py`? | Yes; require it to paste the output | Yes, integrated terminal | No. You run it locally and paste the output back |
| Best at | Long deterministic scripts, PDF wrangling, tests | Many-file UI iteration with live preview | Single-file numerical modules from an exact spec; iterating on `panel.csv` in its code sandbox |
| Watch for | Refactors beyond the task: use plan mode for anything touching more than one file | Agent mode editing outside `web/`: the rule file forbids it; review the diff before accepting | Invented file names and APIs, and its sandbox library versions differing from ours: always give it the file tree and the function signature; re-run locally |
| Session start | Preamble (§11.3) | Preamble (§11.3) | Preamble (§11.3) + upload the current `panel.csv` or the fixture |
| Session end | Validator output pasted, commit | Validator output pasted, commit | You run the validator, paste output back, fix, commit |

**Files the lead creates on Day 0 so the tools behave:**
- `CLAUDE.md`: one line, `@AGENTS.md`.
- `.cursor/rules/agrim.mdc`: frontmatter `description: AGRIM team rules`, `alwaysApply: true`; body = `AGENTS.md` text plus "You may create or edit files only under `web/` and `deck/`."
- `tools/context_pack.py`: writes `CONTEXT_parser.md`, `CONTEXT_findings.md`, `CONTEXT_surface.md`, each = `AGENTS.md` + that component's BUILD.md sections + the relevant schema files + the first 20 rows of the fixture + the repo file tree. Regenerated after any contract change; A uploads the findings one to the ChatGPT Project.

**Working pattern for ChatGPT (A):** one module per chat (for example `m1_slip.py`); paste the spec lines from §7B verbatim; ask for the complete file, not a diff; save it into `findings/models/`; run `pytest findings/tests -q` and `python tools/validate.py` locally; paste failures back verbatim. Use its code sandbox with the uploaded `panel.csv` to check metrics quickly, but the numbers that count are the ones produced locally and committed.

**Working pattern for Cursor (S):** keep `@contracts/` and `@web/public/data/` in context; build each screen against the fixture JSON first; run `npm run build` before every commit; never accept an edit under `contracts/` or `findings/`.

**Working pattern for Claude Code (P):** one adapter per session; paste the page's extracted text into the test fixture before writing the adapter; make it print the row count and the three column sums after every run.

**Swapping tools is fine.** If ChatGPT stalls on M1, A can open Claude Code on the same branch; the spec and the validator are unchanged.

---

## 12. Failure modes and mitigations

| # | Failure | Mitigation (already in the plan) |
|---|---|---|
| 1 | 705526 is a restatement, not an error, and the opener collapses | Lead reads both rows in context on Day 0; fallback opener is the `EXP_DECREASE` class |
| 2 | Parser stalls below 95% | Coverage is displayed, not hidden; an unparsed row cannot produce a false positive; freeze coverage work on Day 5 |
| 3 | Schema drift across the five months | One adapter per month, one `normalize()`, `parse_flags` for every variant |
| 4 | An agent invents fields or output is non-deterministic | `additionalProperties: false`, enums, double-run diff in `validate.py`, single-threaded models |
| 5 | Numbers hardcoded in UI or deck; April figures stale vs July | Literal grep in the validator; `deck/numbers.json`; show April and July side by side (the PS itself anchors April) |
| 6 | Three-way stitch fails again | Checkpoint #1 on Day 1 with fixture data, when reassignment costs one evening |
| 7 | Demo laptop has no data, no network, wrong Python | PDFs and outputs committed; `RUN_DEMO.bat`; cold-machine rehearsal Day 6; second laptop |
| 8 | Deck built last and badly | Deck is S's named deliverable from Day 3; exported Day 5; three timed runs Day 6 |
| 9 | The panel scores AI-feature count, not substance | M1–M4, SHAP, the LLM briefs and the model card are all on screen with the PS's own vocabulary; the comparison table is the second beat of the pitch |
| 10 | Exits mis-stated as cancellations | Enum names say `LAST_SEEN_*`; the screen carries the caveat line; the wording rule in §7 |
| 11 | The May–Jul URLs change or the mirror re-hashes files | Fetch once on Day 0, commit, never fetch again |
| 12 | **Label leakage** makes the model look brilliant | Feature builder computes from snapshots ≤ t0 only; a unit test mutates t1 and asserts features unchanged; the shuffle control must sit at the base rate |
| 13 | **Too few positives in Jun→Jul** to say anything | Report P3 as the second test pair; print `positives` everywhere; if under 30, the slide says so and leads with M2 and M3, which have thousands of rows |
| 14 | **Logistic regression beats gradient boosting** | Show it. That is the PS's dimension (b) answered; the sentence template already handles it |
| 15 | **Models run non-deterministically** across laptops | `random_state=0`, `OMP_NUM_THREADS=1`, outputs committed from one machine (A's), validator diff |
| 16 | **Ollama is not installed, not running, or the laptop lacks RAM** | Briefs are generated once on P's laptop and committed; the dashboard never calls the model on the demo path; live mode hides itself |
| 17 | **An LLM brief contains a number that is not in the ledger** | Grounding check rejects it, regenerates, then falls back to the template; `grounded` is visible on screen |
| 18 | **A model claim is overstated on a slide** | Every model number on a slide must exist in `deck/numbers.json`, which the validator checks against `models.json`; the sentence template names the baseline |
| 19 | **Time runs out with models half-done** | Cut order D41; the audit demo path is unchanged by any cut because model outputs are additive (D40) |

---

## 13. After 12 September

**Phase 2 (to 15 Sept, national PDF):** the same six slides, tightened; add the internal-round judges' feedback visibly; keep the architecture flowchart and the comparison table load-bearing; no new code except bug fixes.

**Phase 3 (Oct–Dec, if shortlisted):** ingest the 15-month archive from ipm with pinned checksums (certificate handled explicitly, dated) → 16 training pairs; a censoring-aware time-to-slip model (lifelines Kaplan–Meier and Cox, with exits as censoring) as the survival complement to M1; full Disclosure Lag; Model A vs B extended with WPI and rainfall series if reachable; FastAPI serving the same JSON plus a PAIMANA-API ingest stub; live Ollama assistant grounded on the ledger; a monthly re-scoring job as each new Flash Report lands. Each is a slide today.

---

## 14. Items only a human can close (this week)

1. **SPOC:** which deadline governs (15 vs 30 Sept); has the college nominated; how the 12 Sept round is scored; the internal cap.
2. **Team composition:** SIH needs six members from one college with at least one female member. This plan assumes three builders; the other members, if any, own primary research (one call with a PMG/IPMD-adjacent officer or a PSU project manager is a documented trump card in the winner corpus), deck polish, and the question bank.
3. **GitHub:** create the private repo and add all three; agree the branch names above.
4. **Lead, Day 0:** the 705526 check; run `fetch_pdfs.py`; commit; confirm `validate.py` green on a fresh clone.
5. **P's laptop:** confirm at least 8 GB RAM, install Ollama, pull `qwen2.5:3b` (about 2 GB download, tonight while other things run).
6. **A:** a ChatGPT Project with the context pack uploaded; a Plus plan for the week if the free-tier code-sandbox limit bites (the limit is reported, not verified).

---

## 15. Not verified in this document

- That pdfplumber's `lines` strategy actually beats 87% on these PDFs (no PDF on disk today; first real evidence is P's Day-1 run).
- The May–Jul 2026 URLs were HEAD-checked by a research agent, not by me; sizes above are theirs.
- The DataMeet GeoJSON path and its boundary vintage.
- `vite-plugin-singlefile` as a `file://` fallback.
- Whether Table 6 has section-header rows or a commissioned-projects list (P's Day-1 checks).
- Whether the 705526 figure has a printed explanation.
- The number of positives in the Jun→Jul pair; the 599-per-four-months figure is from the Dec→Apr join in a transcript, and monthly rates may be much lower or bursty.
- HistGradientBoosting byte-level determinism under threading (undocumented; we force one thread and diff).
- ChatGPT free-tier upload and sandbox limits (help pages were unreachable; secondary sources only).
- That Cursor reads a root `AGENTS.md` without a rule file (secondary source; the `.mdc` rule file is the verified path and is created regardless).
- Team size, female member, SPOC dates.
