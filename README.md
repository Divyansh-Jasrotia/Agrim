# 🏛️ AGRIM — SIH 2026 (Problem Statement: SIH26103)

> **Reporting-Integrity Audit & Early-Warning Overrun Prediction over MoSPI Flash Reports**  
> *An end-to-end data auditing, econometric forecasting, and offline-first intelligence platform for central sector infrastructure projects.*

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.x-646cff.svg)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5%2B-f7931e.svg)](https://scikit-learn.org/)
[![Pytest](https://img.shields.io/badge/Tests-Pytest-0a9edc.svg)](https://pytest.org/)

---

## 📌 Executive Summary

Every month, the **Ministry of Statistics and Programme Implementation (MoSPI)** publishes Flash Reports tracking hundreds of central sector infrastructure projects (each valued at ₹150+ crore). These mega-projects often experience severe schedule slippages, cost escalations, arithmetic anomalies, and delayed milestone disclosures.

**AGRIM** delivers a **three-tier intelligence architecture**:
1. **Deterministic Reporting-Integrity Audit**: Mechanically checks multi-snapshot project data to identify arithmetic contradictions, vanishing projects, and reporting staleness with exact PDF page citations.
2. **Predictive Machine Learning**: Out-of-time validated forecasting models that predict upcoming schedule revisions (slip-filing), estimate progress trajectories, and isolate cost overrun drivers.
3. **Offline Generative Project Briefs**: Local, ledger-grounded LLM synthesis (via Ollama) producing structured risk summaries with zero hallucination risk.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                            INGESTION & PARSING LAYER                              |
|   MoSPI Monthly Flash Report PDFs (Dec 2025, Apr - Jul 2026)                      |
|   -> PDF Table Extractor -> Schema Normalizer -> Multi-Month Panel Builder       |
+-----------------------------------------------------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                                                               |
         v                                                               v
+------------------------------------+          +------------------------------------+
|    DETERMINISTIC AUDIT LAYER       |          |     PREDICTIVE ML LAYER            |
|                                    |          |                                    |
| [F1] Contradiction Ledger          |          | [M1] Slip-Filing Classifier        |
|      (Cumulative exp / progress    |          |      (Predicts upcoming deadline   |
|       drops with page citations)   |          |       revisions before filed)      |
| [F2] Exit Ledger                   |          | [M2] Progress Forecaster           |
|      (Vanishing uncommissioned)    |          |      (Physical progress run-rate)  |
| [F3] Unreachable-DoC Warning       |          | [M3] Overrun Driver Analysis       |
|      (Burn-rate vs stated finish)  |          |      (Econometric peer benchmark)  |
| [F4] Transparent Risk Score (0-100)|          | [M4] Statistical Anomaly Detector  |
| [F5] Field-Information Audit       |          |      (Improbable state shifts)     |
|      (Round-number clustering)     |          |                                    |
+------------------------------------+          +------------------------------------+
         |                                                               |
         +-------------------------------+-------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        OFFLINE LLM & PRESENTATION LAYER                           |
|                                                                                   |
|  * Ollama-Powered Project Risk Briefs (Strict ledger grounding, zero-network)     |
|  * React + TypeScript + TanStack Table v8 Web Console                             |
|  * One-Click Offline Demonstrator (RUN_DEMO.bat)                                  |
+-----------------------------------------------------------------------------------+
```

---

## 🔍 Core Capabilities & Findings

### 1. Deterministic Audit Findings (Shipped as Code)
- **Contradiction Ledger (`findings/contradictions.py`)**: Identifies arithmetic violations between consecutive monthly reports (e.g., cumulative expenditure falling without de-scoping, physical progress percentage dropping). Every finding includes traceable PDF page and table references.
- **Exit Ledger (`findings/exits.py`)**: Flags projects that suddenly disappear from monthly panels without formal commissioning records.
- **Unreachable-DoC Early Warning (`findings/early_warning.py`)**: Mechanically compares current physical progress velocity against remaining time to the stated Date of Completion (DoC).
- **Field-Information Audit (`findings/field_audit.py`)**: Detects abnormal round-number and terminal-digit clustering in self-reported physical progress (digit bias analysis) and flags agency disclosure staleness.
- **Explainable Risk Scoring (`findings/risk.py`)**: Computes an un-blackboxed 0–100 composite risk score with discrete, verifiable trigger reasons.

### 2. Predictive Machine Learning Models
- **Slip-Filing Classifier**: Employs `HistGradientBoostingClassifier` and Logistic Regression to predict which projects will file a delayed completion date in the subsequent reporting cycle.
- **Progress Forecaster**: Multivariate regression forecasting actual physical progress achieved next month.
- **Overrun Driver Analysis**: Econometric models replicating and extending infrastructure benchmark literature (e.g., Ram Singh empirical models) to identify structural cost-escalation factors.
- **Statistical Anomaly Detector**: Flags multi-variable shifts that are arithmetically possible but statistically abnormal across agency distributions.

### 3. Generative Risk Briefs (Ollama)
- Generates executive risk summaries for top-flagged projects using locally hosted open LLMs.
- Every assertion is verified number-by-number against the extracted fact sheets before rendering, eliminating hallucination.

---

## 📂 Repository Structure

```
.
├── contracts/          # Strict typed data schemas, project records & validation bounds
├── data/               # Normalized MoSPI monthly panel data & cached fixtures
├── deck/               # SIH official presentation deck & slide materials
├── docs/               # Full architectural specifications (BUILD.md) & relay logs
├── findings/           # Deterministic audit engines, contradiction ledgers & risk models
│   ├── models/         # Scikit-learn predictive models, feature engineering & benchmarks
│   ├── contradictions.py
│   ├── early_warning.py
│   ├── field_audit.py
│   └── risk.py
├── parser/             # PDF extraction pipeline, table parsing & schema adapters
├── tests/              # Comprehensive Pytest test suites (unit, integration, contracts)
├── tools/              # Dataset validation, schema exporters & verification scripts
├── web/                # React 19 + TypeScript + Vite + TanStack Table web dashboard
├── pyproject.toml      # Project metadata & Python dependencies
├── requirements.lock   # Pinned reproducible dependency lockfile
└── RUN_DEMO.bat        # 1-Click offline demo launcher
```

---

## 🚀 Quick Start & Local Execution

### 1. One-Click Offline Demo (No Internet / No Node required)
Simply double-click or run:
```powershell
.\RUN_DEMO.bat
```
This serves the pre-built web console and pre-computed panel findings locally on your browser.

### 2. Python Development Setup

```powershell
# Create and activate virtual environment (Python 3.12)
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1

# Install locked dependencies
uv pip install -r requirements.lock

# Run test suite
pytest -q

# Validate datasets and contracts
python tools/validate.py
```

### 3. Web Console Development

```powershell
cd web
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🛠️ Technology Stack

- **Core Analytics & ML**: Python 3.12, Scikit-Learn, NumPy, Pandas, SHAP
- **Data Quality & Testing**: Pytest, Pydantic, Custom Contract Validators
- **Frontend Dashboard**: React 19, TypeScript, Vite, TanStack Table v8, Tailwind CSS
- **Generative AI**: Ollama (local offline models for factual risk briefs)

---

## 📜 License

Developed for **Smart India Hackathon (SIH 2026)** — Problem Statement SIH26103.