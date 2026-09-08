# Slide 1 — TITLE PAGE
- Problem Statement ID: SIH26103
- Problem Statement Title: Use case on web-based integrated project-monitoring platform
- Theme: Smart Automation · PS Category: Software
- Team ID / Team Name: (as registered on the portal)

# Slide 2 — IDEA TITLE / Proposed Solution
- AGRIM: a reporting-integrity audit and early-warning prediction layer over MoSPI's own monthly Flash Reports.
- Across the five Flash Reports we parsed (2025-12 to 2026-07) we found 967 arithmetic impossibilities in the Ministry's own published numbers — spread over those five reports, not all inside one of them — e.g. project 705410: cumulative expenditure ₹89,486.62 crore in one report, ₹2,384.29 crore in the next (185 such projects).
- Audit layer (no model): contradiction ledger, exit ledger (443 projects left the panel), unreachable-date early warning (1289 projects), field-information audit, transparent risk score — the 2026-07 panel itself holds 1775 projects.
- Prediction layer (open-source scikit-learn): slip-filing classifier tested on the report it never saw (recall@100 0.28 vs 0.15 for logistic regression), next-month progress forecaster (MAE 1.5 vs 2.3 for linear extrapolation), overrun drivers and peer benchmark (OLS vs gradient boosting), and 134 statistical outliers from an isolation forest — model output, shown beside the rule-based ledger and never counted into its total.
- Innovation: the headline is a verifiable fact in the sponsor's own PDF; every model is shown beside the conventional method with its positives count; every number carries a page citation.

# Slide 3 — TECHNICAL APPROACH
- Flow: PAIMANA PDFs (API in production) → pinned fetch + checksums → per-month adapter parser (pdfplumber) → canonical panel → findings engine (F1–F6) → single feature builder → models M1–M4 → offline LLM briefs with a number-level grounding check → static JSON bundle validated by JSON Schema → React/ECharts dashboard. Target deployment: NIC cloud; no data leaves the ministry.
- Stack (all open source): Python, pdfplumber, PyMuPDF, pandas, scikit-learn, SHAP, Ollama (qwen2.5:3b), jsonschema, React, TypeScript, ECharts, Tailwind.
- Validation: out-of-time split (train Dec 2025–Jun 2026, test Jul 2026); label-shuffle control; determinism gate.

# Slide 4 — FEASIBILITY AND VIABILITY
- Runs today on five public reports with 100% parse coverage of the latest; one laptop, no network, no login.
- Held-out July: n = 1732, projects that filed a revision = 334; on the report-only feature set A, gradient boosting scores PR-AUC 0.61 against 0.35 for logistic regression — the gain is the model family, not extra features.
- The audit features (set B) cost nothing and did not help on this pair: PR-AUC 0.59 against 0.61 for set A, with precision and recall at 100 identical to set A. We report the lower number rather than quote the one that flatters us.
- Risks stated: labels are reporting events; the panel is survivor-selected (exits excluded and counted); the Common Upload Form is behind login, so feature-set A vs B is our answer to dimension (c); cost escalation has too few events to forecast, so it is a driver analysis.
- Mitigations: audit layer independent of models; every metric printed with its positives count; model card on screen.

# Slide 5 — IMPACT AND BENEFITS
- ₹340,503.33 crore of recorded cost overrun in the 2026-07 panel; 967 rule-based arithmetic contradictions across the five reports parsed, which nobody currently flags; 443 projects left the panel across the period without a public reason.
- What an IPMD officer uses Monday: the 100-project watchlist, the contradiction ledger with page citations, the one-click monthly review pack.
- Beneficiaries: IPMD/MoSPI, 17 line ministries, implementing agencies whose reporting quality becomes visible; public accountability through a reproducible audit.

# Slide 6 — RESEARCH AND REFERENCES
- MoSPI Flash Reports Apr–Jul 2026 and Dec 2025 (mospi.gov.in publications); PAIMANA portal; PS SIH26103 text.
- Ram Singh (2009, 2011) on delays and cost overruns — the OLS baseline we replicate.
- The Wire (29 May 2026) and ABC Live (2026) on PAIMANA reporting; PIB monthly releases; Standing Committee on Finance (Aug 2026).
- scikit-learn, SHAP, Ollama documentation; DataMeet India maps (CC BY 4.0).
