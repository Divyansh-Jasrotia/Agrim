# AGRIM — 3-minute pitch (one presenter; operator drives the demo silently)

## 0:00–0:20 — The fact
"In the Ministry's own April report, project {opener_code} shows cumulative expenditure falling — from ₹{opener_before_cr} crore to ₹{opener_after_cr} crore. That is a field that can only go up. Nobody flagged it. It is one of {contradictions_total} arithmetic impossibilities we found across the reports — {count_EXP_DECREASE} of them this same kind."
(Operator: `#/ledger?type=EXP_DECREASE`, then `#/project/{opener_code}`, then Source page. The presenter reads `opener_before_cr`, `opener_after_cr`, `contradictions_total` and `count_EXP_DECREASE` aloud in words, taken from `deck/slides.md`.)

## 0:20–1:35 — The demo
- Ledger → project page → source PDF page ("their own PDF").
- Outlook card: "and the model's separate view, with its five reasons — never blended with the risk score above it."
- `#/predict`: "We trained on December to June and tested on July, a report the model never saw. Gradient boosting against logistic regression, side by side. The audit features added this much."
- `#/exits`: "{exits_total} projects left the panel. Leaving the panel is a change in what got published, not proof of why — the report prints how many were newly commissioned in the same window."
- `#/assistant`, question 8.

## 1:35–2:05 — The model beat
"Same words as every other team — gradient boosting, SHAP, an LLM. Three differences you can check: we tested on the report the model never saw; we show the conventional method even where it wins; every metric carries its positives count."

## 2:05–2:30 — Impact
Slide 5 numbers. "What the officer uses Monday: the watchlist and the review pack."

## 2:30–2:48 — How
"Five public PDFs, deterministic audit, scikit-learn models, all open source, deployable on NIC. Next: the survival model on the sixteen-month archive."

## 2:48–3:00 — Limits, before they are asked
"We audit the record, not the concrete. The upload form is behind login; the model card says what we cannot see."

## Question bank (one owner each)
Why this PS · How is this different from an AI dashboard · Isn't a revised date just paperwork · Where did the exited projects go · Does it need PAIMANA access · The CUF question (set A vs B) · What is your accuracy (we report PR-AUC and top-100 recall with positives) · Why not predict cost overrun (too few events) · Why HistGradientBoosting (same family, zero extra dependencies, native NaN, baseline in the same library) · Did you use an LLM (offline briefs; every number in them is checked digit-by-digit against the ledger — that check verifies numbers, not the wording).
