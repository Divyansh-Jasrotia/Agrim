# AGRIM frontend brief — hand this whole file to the frontend tool

Everything below is context the tool does not have. Paste all of it.

---

## 1. What you are building

**AGRIM** is a reporting-integrity audit and early-warning dashboard over India's public infrastructure project data. It is a hackathon entry for Smart India Hackathon problem statement **SIH26103**, sponsored by **MoSPI** — the Ministry of Statistics and Programme Implementation.

MoSPI publishes a monthly **Flash Report** PDF covering every central-government infrastructure project costing ₹150 crore or more — 1,775 projects as of July 2026, ₹37.11 lakh crore of revised cost. We parsed five of those PDFs (December 2025, and April, May, June, July 2026) at 95–100% row coverage and built a month-by-month panel.

Two things run on that panel:

**The audit layer** finds places where the government's own reports contradict each other between consecutive months — cumulative expenditure that falls when a cumulative figure cannot fall, physical progress that goes backwards, projects that silently disappear from the panel, completion dates that cannot be reached at the project's own reported pace. Every finding cites the exact PDF page it came from, and we ship a rendered image of that page.

**The prediction layer** forecasts which projects will file a revised completion date next month, using gradient boosting, shown side by side with a conventional logistic regression baseline **and** a label-shuffled control, validated on the July report the model never saw.

**The thing that makes this entry different from its rivals** is that all of it runs on real published government data with page citations, while competing entries run the same algorithms on synthetic seed data. The interface must make that difference visible. Provenance is the product.

**The audience** is a panel of judges that may include MoSPI officials. The tone is institutional and audit-like, never marketing.

---

## 2. Hard constraints — breaking any of these breaks the demo

1. **Fully offline.** The demo runs on a laptop with Wi-Fi switched off, served by `python -m http.server 8080 -d web/dist`. **No CDN, no Google Fonts, no external image, no runtime fetch to anything but the local JSON files.** Fonts must be bundled via `@fontsource` npm packages, not a stylesheet link.
2. **Keep the stack.** Vite 8 + React + TypeScript + Tailwind v4 (via `@tailwindcss/vite`, no config file), `react-router-dom` v6, TanStack Table v8 + TanStack Virtual for large tables, Apache ECharts 6 (`echarts-for-react`) for every chart. Do not swap in Recharts, Chart.js, Next.js, shadcn/ui, or a component library.
3. **Hash routing.** URLs look like `#/project/705410`. The operator deep-links mid-demo. Do not use browser history routing.
4. **Data loads from static JSON** in `/data/*.json` relative to the app root, validated against JSON Schema with **Ajv** at load time. If a contract check fails the app must refuse to render and print which key failed — do not "fix" a mismatch by guessing or by falling back to defaults.
5. **No hardcoded data values.** Every number on screen comes from the JSON at runtime. Never type `1775` or `1,101` into a component.
6. **Light theme only.** Projectors wash out dark UIs.
7. **Indian number formatting everywhere.** `Intl.NumberFormat('en-IN')`. Currency reads `₹ 37,10,641.55 cr`. Lakh/crore grouping, never Western thousands grouping.
8. **The word is "contradictions", never "impossibilities".** This is a deliberate accuracy decision. Some flags are true impossibilities and some are strong implausibilities; "contradictions" is correct for all of them and survives a hostile question.
9. **No animation beyond a 150–200 ms fade.** No scroll animation, no bounce, no scale-on-hover.

---

## 3. Design tokens — use these exact values

```css
--color-ground:   #F4F6F8;  /* page background */
--color-surface:  #FFFFFF;  /* cards, tables */
--color-ink:      #0E1A2B;  /* primary text */
--color-muted:    #4B5A6B;  /* secondary text, labels */
--color-line:     #D5DCE4;  /* borders, grid lines */
--color-accent:   #1F5FA8;  /* links, selected state, primary button */
--color-critical: #B42318;
--color-high:     #C2410C;
--color-medium:   #B7791F;
--color-ok:       #1E7B4F;
--color-model:    #5B4B9A;  /* ANY model-derived number */
```

- **Type:** IBM Plex Sans for UI, IBM Plex Mono for project codes and every numeric column, with `font-variant-numeric: tabular-nums`. 15px base, 1.5 line height. Bundle both via `@fontsource/ibm-plex-sans` and `@fontsource/ibm-plex-mono`.
- **Spacing scale:** 8 / 12 / 16 / 24 px. Table rows 36px.
- **Colour rule, absolute:** critical / high / medium / ok encode **severity only**. Never decorative. A falling trend line is never drawn in the `ok` green — that currently happens and it is a bug you are fixing.
- **The model colour rule, absolute:** every number produced by a model is rendered in `--color-model` and carries the word "model" beside it. A judge must never confuse a measured figure with a predicted one. Rule-based scores and model probabilities are shown as separate columns and are **never blended into one number.**
- **Severity is encoded twice** — a colour chip *and* the word. Never colour alone.

---

## 4. Three reference sites, and what to take from each

**Do not** build a generic SaaS analytics dashboard. Build something that reads like an audit institution published it.

### 4.1 World Bank Projects & Operations — `projects.worldbank.org`
The closest domain analogue: a public database of infrastructure and development projects, each with a record page carrying financials, dates, status and an attached document trail.

**Take:** the project page treated as a **record**, not a dashboard card. Identifiers shown prominently and monospaced. Financials in a plain table rather than tiles. A visible document trail proving where each figure came from. Restrained, institutional, information-first.

### 4.2 ICIJ Offshore Leaks Database — `offshoreleaks.icij.org`
An investigative database of entities, built by journalists who must be unimpeachable about what their data does and does not prove.

**Take:** two things. First, the **entity page layout** — dense identity block at the top, then relationships, then sources, with provenance attached to every record. Second, and more important, their **caveat discipline**: their About page states plainly that duplicates are possible and that many listed activities are perfectly legal. AGRIM needs the equivalent, visible wherever flags appear: **"A contradiction is not an allegation."** Put it in the interface, not in a footnote.

### 4.3 UK National Audit Office — `nao.org.uk/report_types/interactive-visualisation/`
A national audit office publishing findings for a parliamentary audience.

**Take:** the visual language of audit — muted palette, heavy use of tables, one interpretive sentence above each chart rather than a bare chart, and **raw CSV published alongside every visualisation**. Add a "download this table as CSV" affordance to every table in AGRIM. It reads as audit rather than marketing, and it costs nothing.

**Supporting references if you want more:** the FT Visual Vocabulary for choosing a chart form by the *relationship* being shown (deviation, ranking, magnitude, change over time) rather than by habit; the GOV.UK and ONS design systems for statistics-publishing chrome and zero-baseline discipline.

### 4.4 What to avoid — the specific tells

Purple-to-cyan gradients. Glassmorphism and frosted cards. Oversized rounded cards floating on a coloured field. A hero section inside a dashboard. A grid of KPI tiles that fills space without supporting a decision. Donut charts. Emoji. Eyebrow labels and vague product copy. Bounce or scale hover animation.

**And the specific failure of the current build:** every panel is the same bordered white card, stacked in three identical two-column grids, so the strongest evidence on the page carries the same visual weight as a collapsed accordion. Vary weight deliberately — one lede, then dense evidence, then quiet supporting notes.

---

## 5. The data contract

Four files load from `/data/`. Field names below are exact. `null` means "the government did not print this value" — it never means zero. **Render `null` as an em dash, never as 0 and never as "NA".**

### `projects.json` — a JSON **array** of project objects

```jsonc
{
  "project_code": "705410",                    // string, monospace everywhere
  "project_name": "Nangal Dam-Talwara 83.74 km - New broad gauge line",
  "agency_raw": "CAOC/NR NR mor",              // string | null — raw agency string
  "state": "Multi-States (Himachal Pradesh, Punjab)",  // string | null
  "sector": "Railways",                        // string | null — a rollup, label it as one
  "status": "ongoing",                         // "ongoing" | "exited"
  "first_seen": "2025-12",                     // "YYYY-MM"
  "last_seen": "2026-07",
  "snapshots": [                               // one per report the project appears in
    {
      "snapshot": "2026-07",
      "page": 88,                              // page in that month's PDF
      "doc_original": "2027-12",               // original completion date, string | null
      "doc_revised": null,                     // revised completion date, string | null
      "cost_original_cr": 2018.0,              // number | null, in ₹ crore
      "cost_revised_cr": 4076.15,
      "expenditure_cum_cr": 2398.08,           // cumulative — cannot fall
      "physical_progress_pct": 84.0            // 0-100, number | null
    }
  ],
  "flags": [
    {
      "type": "EXP_DECREASE",                  // see the type list below
      "severity": "critical",                  // "critical"|"high"|"medium"|"low"|"info"
      "from_snapshot": "2025-12",              // string | null
      "to_snapshot": "2026-04",
      "first_snapshot": "2025-12",             // earliest month this flag applied
      "occurrences": 1,                        // how many months it persisted
      "before": 89486.62,
      "after": 2384.29,
      "detail": "Cumulative expenditure falls from ₹89,486.62 cr in 2025-12 to ₹2,384.29 cr in 2026-04; a cumulative field cannot decrease.",
      "sources": [{"snapshot": "2025-12", "page": 74}, {"snapshot": "2026-04", "page": 88}]
    }
  ],
  "risk": {
    "band": "red",                             // "red"|"amber"|"yellow"|"green"
    "score": 100,                              // 0-100, RULE-BASED, not a model
    "reasons": ["Cumulative expenditure fell between two reports."]
  },
  "ml": {                                      // object | null — EVERY field here is model-derived
    "slip_prob": 0.121,                        // 0-1, chance of filing a revised date next report
    "slip_rank": 976,
    "slip_top_factors": [                      // SHAP, exactly 5, render as a diverging bar chart
      {"feature": "physical_progress_pct", "contribution": -1.8304, "value": 8.15}
    ],
    "progress_next_pred": 9.7148,              // predicted next-month progress %
    "expected_completion": "2029-04",          // string | null
    "expected_delay_months": 16,               // number | null
    "cost_overrun_residual_pct": 0.7201,       // vs comparable projects
    "peer_expected_cost_overrun_pct": -0.7201,
    "time_overrun_residual_months": -1.1578,
    "peer_expected_time_overrun_months": 1.1578,
    "anomaly_flag": false,
    "anomaly_score": 0.416,
    "scored_at_snapshot": "2026-07"
  }
}
```

**Flag types and what they mean, for writing labels:**

| type | meaning | count |
|---|---|---|
| `EXP_DECREASE` | cumulative expenditure fell between two reports | 185 |
| `PROG_DECREASE` | physical progress went backwards | 158 |
| `EXP_GT_REVISED_COST` | spend exceeds the revised sanctioned cost | 331 |
| `ZERO_PROG_NONZERO_EXP` | money spent, zero progress reported | 285 |
| `DOC_BEFORE_APPROVAL` | completion date precedes the approval month | 8 |
| `STAT_ANOMALY` | **model-derived** outlier from an isolation forest — show last, in model colour, never counted as a contradiction | 134 |
| `DOC_UNREACHABLE` | cannot reach 100% by its own date at its own pace | 1,289 |
| `DOC_REVISED_FILED` | informational: the revised date changed | 1,746 |
| `COST_REVISED_FILED` | informational: the revised cost changed | 180 |
| `DOC_PASSED` | the stated completion date has passed | 345 |

### `findings.json` — a single object

```jsonc
{
  "meta": {
    "contract_version": "1.3.0",
    "generated_at": "2026-09-08T07:35:36+00:00",   // the ONLY timestamp in the system
    "snapshots": ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"],
    "coverage": [{"snapshot": "2026-07", "rows_parsed": 1775, "rows_printed": 1775, "pct": 100.0}],
    "headline": {
      "projects_latest": 1775,
      "cost_revised_total_cr": 3710641.55,
      "overrun_total_cr": 340503.33,
      "contradictions_total": 1101,        // includes statistical anomalies — do NOT headline this
      "contradictions_arithmetic": 967,    // HEADLINE THIS as "contradictions"
      "statistical_anomalies": 134,        // show separately, in model colour
      "exits_total": 443,
      "unreachable_total": 1289,
      "watchlist_size": 100
    },
    "denominators": {                      // projects excluded because a field was not printed
      "cost_revised_null": 0, "cost_overrun_null": 0, "doc_null": 0
    }
  },
  "contradictions": {
    "by_type": [{"type": "EXP_DECREASE", "count": 185}],
    "rows": [ /* flag objects, plus project_code and project_name */ ]
  },
  "exits": {
    "pairs": [{"from": "2026-06", "to": "2026-07", "exited": 78, "entered": 6,
               "commissioned_printed": 9, "exited_cost_revised_cr": 12345.67}],
    "rows": [{"project_code": "…", "project_name": "…", "last_seen": "2026-06",
              "last_progress_pct": 91.0, "last_expenditure_cr": 1200.0,
              "last_cost_revised_cr": 1500.0, "partition": "…", "sources": [] }]
  },
  "early_warning": {
    "rows": [{"project_code": "…", "project_name": "…", "velocity_pct_per_month": 0.26,
              "months_needed": 61, "months_remaining": 17, "ratio": 3.6,
              "severity": "critical", "sources": []}]
  },
  "field_audit": {
    "snapshot": "2026-07",
    "terminal_digit": [{"digit": 0, "count": 517, "share": 0.2913}],   // 10 entries, 0-9
    "whole_number_share": 0.3538,
    "multiple_of_5_share": 0.1651,
    "multiple_of_10_share": 0.1166,
    "whipple_index": 152.4,          // number | null — digit-heaping index, 100 = no preference
    "whipple_band": "rough"          // string | null — UN quality band
  },
  "disclosure_lag": {"status": "computed", "median_lag_months": 2.0,
                     "rows": [{"project_code": "…", "first_unreachable": "2026-04",
                               "filed_at": "2026-06", "lag_months": 2}]},
  "delay_series": {                  // the classification MoSPI stopped publishing after 2014
    "bands": ["on_schedule", "d_1_12", "d_13_24", "d_25_60", "d_61_plus"],
    "rows": [{"snapshot": "2026-07", "on_schedule": 0, "d_1_12": 0, "d_13_24": 0,
              "d_25_60": 0, "d_61_plus": 0, "classifiable": 0, "doc_null": 0}]
  },
  "escalation": {                    // ministries/sectors whose delay rate exceeds the threshold
    "threshold_pct": 50.0,
    "rows": [{"key": "Railways", "projects": 200, "classifiable": 180, "delayed": 120,
              "delay_rate_pct": 66.67, "first_rate_pct": 60.0,
              "improving": false, "escalate": true}]
  },
  "by_state":  [{"key": "Bihar", "projects": 60, "flagged": 41, "red": 9}],
  "by_sector": [{"key": "Railways", "projects": 200, "flagged": 150, "red": 30}],
  "review_pack": [{"project_code": "…", "project_name": "…", "state": "…", "sector": "…",
                   "risk_band": "red", "risk_score": 100, "slip_prob": 0.93,
                   "expected_delay_months": 12, "flag_types": "EXP_DECREASE;PROG_DECREASE",
                   "page": 88}],
  "assistant": [{"id": 1, "question": "…", "answer": "…", "sources": [{"snapshot": "…", "page": 1}]}]
}
```

### `models.json` — a single object

```jsonc
{
  "m1_slip": {
    "results": [{"model_id": "LR_A", "test_pair": "P4", "pr_auc": 0.3472, "roc_auc": 0.682,
                 "precision_at_100": 0.49, "recall_at_100": 0.1467, "lift_at_100": 2.5,
                 "n": 1732, "positives": 334, "base_rate": 0.1928,
                 "calibration": [{"bin": 0, "mean_pred": 0.045, "mean_obs": 0.0858, "n": 431}]}],
    "feature_sets": {"A": ["physical_progress_pct", "…"], "B": ["…", "velocity_pct_per_month", "…"]},
    "importance_HGB_B": [{"feature": "months_to_doc", "mean": 0.3835, "std": 0.0081}],
    "coefficients_LR_A": [{"feature": "cat__sector_Railways", "value": 0.6364}],
    "watchlist": [{"project_code": "618758", "slip_prob": 0.9677, "slip_rank": 1}]
  },
  "m2_progress": {"results": [{"model_id": "ZERO", "mae": 1.6291, "median_ae": 0.09, "n": 1732, "test_pair": "P4"}],
                  "winner": "HGB", "agreement_with_F3": {"n": 27, "share_same_direction": 1.0}},
  "m3_drivers": {"results": [{"model_id": "OLS", "target": "cost_overrun_pct", "cv_r2": 0.152, "cv_mae": 19.7867}],
                 "partial_dependence": [{"feature": "log_cost_original", "target": "cost_overrun_pct",
                                         "grid": [5.22, 5.40], "values": [-3.81, -3.81]}],
                 "sector_effects": [{"sector": "Railways", "n": 200, "effect_cost_pct": -3.67, "effect_time_months": -2.28}],
                 "n": 1775, "snapshot": "2026-07"},
  "m4_anomaly": {"contamination": "auto"},
  "meta": {"test_pair": "P4"}
}
```

`model_card.json` also exists and renders as a single printable column on `#/model-card`.

**Model IDs, for the comparison table:** `LR_A` is logistic regression on feature set A (the conventional baseline). `HGB_A` and `HGB_B` are gradient boosting on sets A and B. `HGB_B_SHUFFLED` is a control run with the labels randomised — it *should* score near the base rate, and its poor score is the proof the pipeline is not leaking. Show all four. Show the baseline even where it wins.

### PDF page images

`/pages/<snapshot>/p<page>.png` — for example `/pages/2026-04/p88.png`. These are rendered images of the actual government PDF page. **They are the single most important asset in this interface.** A flag's `sources[]` gives you the snapshot and page to build the path.

---

## 6. Screens

Ten routes. Every screen: summary first, detail below.

**Left rail, three groups.** *Audit*: Overview `#/`, Contradiction Ledger `#/ledger`, Exit Ledger `#/exits`, Field Audit `#/fields`. *Outlook*: Early Warning `#/warning`, Predictions `#/predict`, Drivers & Benchmark `#/drivers`. *About*: Assistant `#/assistant`, Model Card `#/model-card`. Project pages at `#/project/:code` are reached by clicking a row.

**Header, 56px.** A persona switch (national view / single sector — it is a filter over the data), a coverage chip reading "5 reports · 9,4xx rows · 98% parsed", and an "Export review pack" button that downloads `review_pack` as CSV.

| Route | What it shows | The sentence the presenter says over it |
|---|---|---|
| `#/` **Overview** | A stated finding as a sentence, not a tile grid. Then the contradiction types as a ranked bar, an India map shaded by flagged count per state, and a table of the highest-risk projects **sorted by model probability** (sorting by rule score makes the column constant at 100 and useless). | "Five public reports, parsed. Every number here has a page." |
| `#/ledger` **Contradiction Ledger** | Table grouped by type. Columns: project, months, before → after, delta, severity, page. Filter chips by type, arithmetic types first and `STAT_ANOMALY` last and visually separated. Row click → project. | "A cumulative field cannot go down. Here are the ones that did." |
| `#/project/:code` **Project** | **The signature screen.** See §7. | — |
| `#/exits` **Exit Ledger** | A waterfall per month pair showing exited vs entered, and a table of exits with each project's last observed state. Caveat line: these are net changes; the reason a project left is behind a login. | "443 projects left the panel. The report says nine were commissioned." |
| `#/warning` **Early Warning** | Table sorted by `ratio` with a plain sentence per row, plus a distribution chart of the ratio. | "No model here. Their own two numbers disagree." |
| `#/predict` **Predictions** | **The second signature screen.** See §7. | — |
| `#/drivers` **Drivers & Benchmark** | Partial-dependence lines per target, sector effect bars, a scatter of expected vs actual overrun, and the **escalation matrix** table from `findings.escalation` — sectors above the 50% delay threshold that are not improving. Label the sector field as an agency-string rollup, not the 17 official ministries. | "What drives overrun, and which ministries a committee would escalate." |
| `#/fields` **Field Audit** | Terminal-digit histogram with a uniform reference line, the **Whipple index** and its band called out as a named statistic, and staleness by agency. | "Which of your fields are measured, and which are guessed." |
| `#/assistant` **Assistant** | The eight fixed questions from `findings.assistant` with answers and source chips, plus project-code lookup. | "It answers only from the ledger, with a page for every number." |
| `#/model-card` **Model Card** | `model_card.json` rendered as one printable column. | "Everything we cannot see, stated." |

---

## 7. The two screens to over-invest in

### 7.1 `#/project/:code` — the evidence block

This is 30 of the 95 demo seconds and it is the thing no rival has. Currently it is six identical cards in three two-column grids, and the strongest evidence is buried. Restructure it:

**Top, full width — the evidence block.** Take the project's highest-severity flag and give it the whole width. The `detail` sentence in display type. **The rendered PDF page image inline, at a size where the row is actually readable — not hidden behind a small chip.** The parsed value called out beside it, so the viewer sees the government's printed page and our number at the same time. For project `705410` this reads: *cumulative expenditure falls from ₹89,486.62 cr in December to ₹2,384.29 cr in April; a cumulative field cannot decrease* — beside the actual page from each PDF.

**Below, at clearly lower visual weight:** the two sparklines (progress and cumulative expenditure across snapshots, with the model's forecast tail in `--color-model`); the remaining flags as a list; the Outlook card (slip probability, the five SHAP factors as a proper diverging bar chart with a zero line, expected completion vs stated date, peer benchmark); the cached LLM brief with its "verified against ledger" chip; and the "As printed, by report" table — one row per snapshot, every figure exactly as the PDF printed it.

**Fix while you are here:** the expenditure sparkline currently draws that collapse in `#1E7B4F`, the `ok` green. A catastrophic drop must never render in the reassuring colour.

### 7.2 `#/predict` — the comparison table

This is the answer to the problem statement's "AI vs conventional methods" requirement, and it is already the strongest screen. Do not restructure it — sharpen it.

- The comparison table carries `LR_A`, `HGB_A`, `HGB_B`, `HGB_B_SHUFFLED` against PR-AUC, ROC-AUC, precision@100, recall@100, lift@100.
- **Print `n` and `positives` in the column header itself**, not only in prose above.
- Mark the winning row, and keep the losing baseline fully visible. Showing the conventional method even when it loses is the point.
- Keep the honesty caveat below the table and give it real weight rather than fine print.
- Below: the PR curve, the calibration plot, and the 100-project watchlist with columns for project, probability, rank, top factor, rule band, expected delay, and page.

---

## 8. Definition of done — six conditions, checked on a screenshot of every route at 1440×900

1. **No number wraps across lines.** `₹ 37,10,641.55 cr` fits on one line. This currently breaks across three lines and is a defect you are fixing.
2. **No dead column.** No table column shows the same value in every visible row.
3. **Colour encodes severity only.** No decorative colour. No falling trend in `ok` green.
4. **Every model-derived number is in `#5B4B9A` and carries the word "model".**
5. **One focal point per screen.** Not six equal cards.
6. **Provenance on everything.** Every figure either traces to a page citation or is explicitly labelled model-derived.

**Mechanical checks that must also pass:**

```bash
# Nothing external — the demo runs with Wi-Fi off
grep -rEoh "https?://[^\"' )]+" dist/assets/*.js dist/assets/*.css dist/index.html | sort -u
# expected: no output

# No hardcoded data values
grep -rEn "1775|1101|967|443|1289|3710641|340503" src/
# expected: no output
```

And: corrupt `data/findings.json` on purpose and confirm the app **refuses to render and names the failing key** rather than showing a blank screen or silently defaulting.

---

## 9. The demo path

The operator rehearses this exact 95-second sequence. Every screen in it must be fast and deep-linkable:

`#/` (5s) → `#/ledger` filtered to `EXP_DECREASE` (15s) → `#/project/705410`, open the source page, then the Outlook card (30s) → `#/predict`, comparison table then watchlist (25s) → `#/exits` (15s) → `#/assistant` (5s).
