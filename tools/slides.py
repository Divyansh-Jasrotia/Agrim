"""Render deck/slides.md: the text of the six official-template slides with every number from deck/numbers.json.
Run: python tools/slides.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = """# Slide 1 — TITLE PAGE
- Problem Statement ID: SIH26103
- Problem Statement Title: Use case on web-based integrated project-monitoring platform
- Theme: Smart Automation · PS Category: Software
- Team ID / Team Name: (as registered on the portal)

# Slide 2 — IDEA TITLE / Proposed Solution
- AGRIM: a reporting-integrity audit and early-warning prediction layer over MoSPI's own monthly Flash Reports.
- In the Ministry's own {latest_snapshot} report we found {contradictions_total} arithmetic impossibilities across {projects_latest} projects — e.g. project {opener_code}: cumulative expenditure ₹{opener_before_cr} crore in one report, ₹{opener_after_cr} crore in the next ({count_EXP_DECREASE} such projects).
- Audit layer (no model): contradiction ledger, exit ledger ({exits_total} projects left the panel), unreachable-date early warning ({unreachable_total} projects), field-information audit, transparent risk score.
- Prediction layer (open-source scikit-learn): slip-filing classifier tested on the report it never saw (recall@100 {m1_HGB_B_recall_at_100} vs {m1_LR_A_recall_at_100} for logistic regression), next-month progress forecaster (MAE {m2_HGB_mae} vs {m2_OWN_VELOCITY_mae} for linear extrapolation), overrun drivers and peer benchmark (OLS vs gradient boosting).
- Innovation: the headline is a verifiable fact in the sponsor's own PDF; every model is shown beside the conventional method with its positives count; every number carries a page citation.

# Slide 3 — TECHNICAL APPROACH
- Flow: PAIMANA PDFs (API in production) → pinned fetch + checksums → per-month adapter parser (pdfplumber) → canonical panel → findings engine (F1–F6) → single feature builder → models M1–M4 → offline LLM briefs with a number-level grounding check → static JSON bundle validated by JSON Schema → React/ECharts dashboard. Target deployment: NIC cloud; no data leaves the ministry.
- Stack (all open source): Python, pdfplumber, PyMuPDF, pandas, scikit-learn, SHAP, Ollama (qwen2.5:3b), jsonschema, React, TypeScript, ECharts, Tailwind.
- Validation: out-of-time split (train Dec 2025–Jun 2026, test Jul 2026); label-shuffle control; determinism gate.

# Slide 4 — FEASIBILITY AND VIABILITY
- Runs today on five public reports with {coverage_pct_2026-07}% parse coverage of the latest; one laptop, no network, no login.
- Held-out July: n = {m1_HGB_B_n}, projects that filed a revision = {m1_HGB_B_positives}; PR-AUC {m1_HGB_B_pr_auc} (boosting + audit features) vs {m1_LR_A_pr_auc} (logistic).
- Risks stated: labels are reporting events; the panel is survivor-selected (exits excluded and counted); the Common Upload Form is behind login, so feature-set A vs B is our answer to dimension (c); cost escalation has too few events to forecast, so it is a driver analysis.
- Mitigations: audit layer independent of models; every metric printed with its positives count; model card on screen.

# Slide 5 — IMPACT AND BENEFITS
- ₹{overrun_total_cr} crore of recorded cost overrun in the {latest_snapshot} panel; {contradictions_total} inconsistencies nobody currently flags; {exits_total} projects left the panel across the period without a public reason.
- What an IPMD officer uses Monday: the 100-project watchlist, the contradiction ledger with page citations, the one-click monthly review pack.
- Beneficiaries: IPMD/MoSPI, 17 line ministries, implementing agencies whose reporting quality becomes visible; public accountability through a reproducible audit.

# Slide 6 — RESEARCH AND REFERENCES
- MoSPI Flash Reports Apr–Jul 2026 and Dec 2025 (mospi.gov.in publications); PAIMANA portal; PS SIH26103 text.
- Ram Singh (2009, 2011) on delays and cost overruns — the OLS baseline we replicate.
- The Wire (29 May 2026) and ABC Live (2026) on PAIMANA reporting; PIB monthly releases; Standing Committee on Finance (Aug 2026).
- scikit-learn, SHAP, Ollama documentation; DataMeet India maps (CC BY 4.0).
"""


def render(nums):
    text = TEMPLATE
    for k, v in nums.items():
        val = f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
        text = text.replace("{" + k + "}", val)
    return text


if __name__ == "__main__":
    nums = json.loads((ROOT / "deck" / "numbers.json").read_text(encoding="utf-8"))
    out = ROOT / "deck" / "slides.md"
    out.write_text(render(nums), encoding="utf-8")
    print("wrote", out)
