# AGRIM Relay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build AGRIM (SIH26103) — a reporting-integrity audit plus a prediction layer over five public MoSPI Flash Report PDFs — as twenty strictly sequential tasks that any of three people, using any AI coding tool, can pick up from the last ticked checkbox.

**Architecture:** A Python pipeline turns PDFs into one canonical `panel.csv`, then into `projects.json` / `findings.json` / `models.json` / `briefs.json` under `web/public/data/`, all validated against JSON Schemas in `contracts/`. A static Vite + React app reads those files. Nothing runs live on demo day except a local static server. The spec is `docs/BUILD.md` (v2, 5 Sept 2026); this plan implements it in order.

**Tech Stack:** Python 3.12 (uv), pdfplumber, PyMuPDF, pandas 2.x, scikit-learn, shap, jsonschema, pytest; Node 24, Vite 8, React 18, TypeScript, Tailwind v4, ECharts 6, TanStack Table v8, Ajv, react-router-dom v6; Ollama (`qwen2.5:3b`) at build time only.

## Global Constraints

- Repo lives at `C:\dev\agrim` (outside OneDrive). GitHub private repo `agrim`. Default branch `main`.
- Python 3.12 via `uv venv --python 3.12`; install from `requirements.lock`; never `pip install` ad hoc.
- Snapshots in scope, exactly these strings: `2025-12`, `2026-04`, `2026-05`, `2026-06`, `2026-07`.
- Empty CSV cell = NULL = "not printed". Never 0, never "NA". JSON uses `null`.
- The parser never derives (no overruns, deltas, sectors, joins in `panel.csv`).
- Every estimator gets `random_state=0`; `findings/run.py` sets `OMP_NUM_THREADS=1` before importing sklearn; JSON is written with `sort_keys=True` and floats rounded to 4 decimals.
- Model features use only snapshots at or before the pair's first month.
- No network access at runtime anywhere. Network only in `tools/fetch_pdfs.py` (PDFs) and `findings/briefs.py` (local Ollama at build time).
- No numeric literal of three or more digits in `web/src/**/*.ts(x)` or `deck/pitch.md` except years, `px` sizes and hex colours.
- `contracts/` is read-only for every task except Task 2 (creates it) and Task 9 (adds golden fixtures). Contract freeze after Task 9: only additive nullable fields.
- Rule-based risk (F4) and model probability (M1) are never blended.
- Wording rule: projects "left the monitored panel", never "cancelled".
- Every task ends with `python tools/validate.py` exit 0 and `pytest -q` green (from Task 2 on), a commit, and ticked checkboxes in this file.

---

## How the relay works (read before Task 1)

**Order is the contract.** Tasks run 1 → 20. Task N assumes Tasks 1..N−1 are merged to `main`. Nobody starts N+1 while N is unmerged, except to review it.

**Claiming a task.** Before touching code: `git pull`, then add one line to `docs/RELAY.md` under "Claims": `Task 07 — Ranvir — 2026-09-07 19:10 — started`, commit it to `main` directly (`git commit -am "relay: claim task 07" && git push`). If the push is rejected, someone else claimed first: pull and pick the next unclaimed task (which is only ever the next number).

**Branch and PR.** `git switch -c task/07-exits-warning` from `main`. Commit after every green step. When the task's last step is done, push and open a PR titled `Task 07: exits and early warning` with the PR body = the pasted output of `python tools/validate.py` and `pytest -q`.

**Review.** The reviewer is whoever will do Task N+1 (reading the diff is their onboarding). Review checklist: validator output pasted; tests exist and ran; no edits under `contracts/` (unless the task allows); no hardcoded numbers; the plan's checkboxes for the task are ticked in the same PR. One approval, then squash-merge. The author deletes the branch.

**Handing off mid-task.** If you must stop before the task is done: tick the steps you finished in this file, commit, push the branch, open a **draft** PR titled `Task 07 (partial): ...` whose first line is `HANDOFF: stopped after step 4; step 5 fails with <pasted error>`. Add `Task 07 — Ranvir — 2026-09-07 23:40 — handed off at step 4` to `docs/RELAY.md` on `main`. The next person checks out the same branch and continues from the first unticked step.

**Staying current.** Every session starts with `git switch main && git pull`. Contract changes (Task 2 and Task 9 only) are logged in `contracts/CHANGELOG.md`. Generated outputs (`data/out/panel.csv`, `web/public/data/*.json`, `web/dist/`) are committed by the task that produces them so nobody needs another person's machine.

**Tools.** Each task starts with a paste-in preamble for your AI tool (Claude Code, Cursor, ChatGPT, anything). Tools that cannot run commands (ChatGPT) get the commands from you: run them locally and paste the output back. `AGENTS.md` is loaded automatically by Claude Code (via `CLAUDE.md`) and Cursor (via `.cursor/rules/agrim.mdc`); for ChatGPT, upload `AGENTS.md`, `docs/BUILD.md` and this plan to a ChatGPT Project once.

**The preamble** (replace N and the task title):

> Read `AGENTS.md`. Then read `docs/superpowers/plans/2026-09-06-agrim-relay-plan.md`, section "Task N: <title>", and only that section plus "Global Constraints". Do exactly the unticked steps in order. Edit only the files the task lists. When a step says Run, run it (or give me the command and wait for my pasted output). Do not skip the failing-test step. Stop after the commit step and tell me which checkboxes to tick.

---

## File structure (what exists when Task 20 is done)

```
agrim/
  AGENTS.md  CLAUDE.md  README.md  RUN_DEMO.bat  .gitignore
  .cursor/rules/agrim.mdc
  pyproject.toml  requirements.txt  requirements.lock  .python-version
  docs/BUILD.md  docs/RELAY.md  docs/DAY1-CHECKS.md
  docs/superpowers/plans/2026-09-06-agrim-relay-plan.md   <- this file; checkboxes are the shared progress state
  contracts/
    panel.schema.json  projects.schema.json  findings.schema.json  models.schema.json
    briefs.schema.json  model_card.schema.json  enums.json  CHANGELOG.md
    fixtures/make_fixture.py  fixtures/panel.sample.csv  fixtures/synthetic_panel.py
    fixtures/aggregates.json  fixtures/projects.sample.json  fixtures/findings.sample.json
  tools/__init__.py  tools/validate.py  tools/fetch_pdfs.py  tools/show_page.py  tools/render_pages.py  tools/slides.py
  data/pdfs/*.pdf  data/pdfs/SHA256SUMS  data/out/parts/<snapshot>.csv  data/out/panel.csv  data/out/parse_coverage.md
  parser/__init__.py  parser/extract.py  parser/normalize.py  parser/adapters.py  parser/run.py
  findings/__init__.py  findings/panel.py  findings/contradictions.py  findings/exits.py
  findings/early_warning.py  findings/risk.py  findings/field_audit.py  findings/disclosure_lag.py
  findings/assistant.py  findings/features.py  findings/briefs.py  findings/run.py
  findings/models/__init__.py  findings/models/metrics.py  findings/models/m1_slip.py
  findings/models/m2_progress.py  findings/models/m3_drivers.py  findings/models/m4_anomaly.py
  findings/models/model_card.py
  tests/__init__.py  tests/test_env.py  tests/tools/  tests/parser/  tests/findings/  tests/models/
  web/  (Vite app; web/public/data/*.json and web/public/pages/**.png and web/dist/ are committed)
  deck/numbers.json  deck/slides.md  deck/pitch.md  deck/AGRIM-SIH26103.pptx  deck/AGRIM-SIH26103.pdf
```

Responsibilities: `parser/` reads PDFs and writes canonical rows only. `findings/panel.py` is the single loader and date helper. Each `findings/*.py` finding module exposes one `compute`/`detect` function. `findings/features.py` is the only feature builder. `findings/run.py` assembles every JSON. `tools/validate.py` is the only gate. `web/src/data/` is the only place the app touches files.

---

### Task 1: Repository, environment, agent rule files

**Files:**
- Create: `C:\dev\agrim\` (new folder), `.gitignore`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/agrim.mdc`, `pyproject.toml`, `requirements.txt`, `.python-version`, `docs/BUILD.md` (copy), `docs/RELAY.md`, `tools/__init__.py`, `parser/__init__.py`, `findings/__init__.py`, `findings/models/__init__.py`, `tests/__init__.py`, `tests/tools/__init__.py`, `tests/parser/__init__.py`, `tests/findings/__init__.py`, `tests/models/__init__.py`, `tests/test_env.py`
- Copy: this plan into `docs/superpowers/plans/2026-09-06-agrim-relay-plan.md` (it is already there if you cloned; if you are creating the folder, copy it from the research folder)

**Interfaces:**
- Consumes: nothing.
- Produces: an installable repo where `pytest -q` passes; `requirements.lock` for everyone else.

- [x] **Step 1: Create the folder, the venv, and the pins**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force C:\dev\agrim | Out-Null
Set-Location C:\dev\agrim
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1
python --version
```
Expected: `Python 3.12.x`.

Create `requirements.txt`:
```
pdfplumber>=0.11.10,<0.12
pymupdf>=1.28,<2
pandas>=2.2,<3
numpy>=1.26,<3
scikit-learn>=1.6,<2
shap>=0.47
jsonschema>=4.23
pytest>=8
ollama>=0.4
```
(`pandas<3` because the code in this plan is written against the 2.x behaviour of copy-on-write and string dtypes; the `.lock` file below is what teammates install.)

Create `.python-version` containing `3.12`.

Run:
```powershell
uv pip install -r requirements.txt
uv pip freeze | Out-File -Encoding utf8 requirements.lock
```
Expected: no errors; `requirements.lock` lists pinned `==` versions.

- [x] **Step 2: Write the failing environment test**

Create `tests/__init__.py`, `tests/tools/__init__.py`, `tests/parser/__init__.py`, `tests/findings/__init__.py`, `tests/models/__init__.py` (all empty), `tools/__init__.py`, `parser/__init__.py`, `findings/__init__.py`, `findings/models/__init__.py` (all empty).

Create `tests/test_env.py`:
```python
import importlib
import sys


def test_python_version():
    assert sys.version_info[:2] == (3, 12)


def test_required_packages_import():
    for name in ["pdfplumber", "fitz", "pandas", "numpy", "sklearn", "shap", "jsonschema"]:
        importlib.import_module(name)
```

Create `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-q"
```

- [x] **Step 3: Run the test and make it pass**

Run: `pytest -q`
Expected: `2 passed`. If `fitz` fails to import, run `uv pip install pymupdf` and re-freeze the lock.

- [x] **Step 4: Write the rule files every AI tool reads**

Create `AGENTS.md`:
```markdown
# AGENTS.md — rules for every AI tool working in this repo

1. You work on exactly one task from docs/superpowers/plans/2026-09-06-agrim-relay-plan.md. Edit only the files that task lists, plus its tests.
2. contracts/ is read-only unless your task says otherwise. If a field you need does not exist, stop and report; do not add it.
3. Empty CSV cell = NULL = "not printed". Never write 0 or "NA" for a missing value. JSON uses null.
4. Never hardcode a number that comes from the data. The web app and the deck read numbers from JSON.
5. Runs are deterministic: random_state=0 on every estimator, OMP_NUM_THREADS=1 in findings/run.py, JSON written with sort_keys=True and floats rounded to 4 decimals. The only timestamp is meta.generated_at.
6. Model features may use only snapshots at or before the pair's first month. Nothing from the later month is a feature.
7. No network access at runtime. Network only in tools/fetch_pdfs.py and findings/briefs.py (local Ollama, build time).
8. Before you say "done": run `python tools/validate.py` and `pytest -q` and paste the output. Never claim tests pass without the run.
9. New dependency: add it to requirements.txt AND re-freeze requirements.lock (or package.json + package-lock.json) in the same commit.
10. If a spec line in docs/BUILD.md or the plan is ambiguous, implement the literal reading and leave a `# SPEC?` comment. Do not choose a cleverer interpretation.
11. Tick the task's checkboxes in the plan file as steps complete and commit them with the code.
12. Commit messages: `task NN: <what>`.
```

Create `CLAUDE.md` containing exactly one line:
```
@AGENTS.md
```

Create `.cursor/rules/agrim.mdc`:
```
---
description: AGRIM team rules — always on
alwaysApply: true
---
Read AGENTS.md at the repo root and follow it. Work only on the task you were given from docs/superpowers/plans/2026-09-06-agrim-relay-plan.md. Do not edit files under contracts/ unless the task says so. Run `python tools/validate.py` and `pytest -q` before claiming completion and show the output.
```

Create `.gitignore`:
```
.venv/
__pycache__/
.pytest_cache/
*.pyc
node_modules/
web/.vite/
data/out/tmp*/
CONTEXT_*.md
```

- [x] **Step 5: Write README and the relay log**

Create `README.md`:
```markdown
# AGRIM — SIH26103

Reporting-integrity audit and early-warning prediction over MoSPI Flash Reports. Spec: docs/BUILD.md. Plan and progress: docs/superpowers/plans/2026-09-06-agrim-relay-plan.md.

## Run the demo (no network, no Node needed)

    RUN_DEMO.bat

## Develop

    uv venv --python 3.12
    .\.venv\Scripts\Activate.ps1
    uv pip install -r requirements.lock
    pytest -q
    python tools/validate.py
```

Create `docs/RELAY.md`:
```markdown
# Relay log

Rules: see the "How the relay works" section of the plan. One line per claim or handoff, newest at the bottom.

## Claims

Task 01 — <name> — <YYYY-MM-DD HH:MM> — started
```

Copy the spec: `Copy-Item "C:\Users\RANVIR\OneDrive\Desktop\research\sih-2026\BUILD.md" docs\BUILD.md` and, if not already present, the plan into `docs\superpowers\plans\2026-09-06-agrim-relay-plan.md`.

- [x] **Step 6: Initialise git and GitHub, first commit**

Run:
```powershell
git init -b main
git add -A
git commit -m "task 01: repo skeleton, env, agent rules"
gh repo create agrim --private --source . --remote origin --push
```
Expected: repo visible at github.com/<you>/agrim. Then in GitHub → Settings → Collaborators, add the other two. Recommended branch rule on `main`: require a pull request with one approval (Settings → Rules → New ruleset).

---

### Task 2: Contracts, enums, fixtures, and the validator

**Files:**
- Create: `contracts/panel.schema.json`, `contracts/projects.schema.json`, `contracts/findings.schema.json`, `contracts/models.schema.json`, `contracts/briefs.schema.json`, `contracts/model_card.schema.json`, `contracts/enums.json`, `contracts/CHANGELOG.md`, `contracts/fixtures/make_fixture.py`, `contracts/fixtures/panel.sample.csv` (generated), `contracts/fixtures/synthetic_panel.py`, `tools/validate.py`
- Test: `tests/tools/test_contracts.py`, `tests/tools/test_validate.py`

**Interfaces:**
- Consumes: Task 1 environment.
- Produces: the schemas every later task validates against; `python tools/validate.py` (exit 0/1; steps SKIP when their inputs do not exist yet); `contracts/fixtures/panel.sample.csv` (12 projects × 5 snapshots); `synthetic_panel.write(path, n_projects=600, seed=0)` for model tests. Column order of `panel.csv` is the `COLUMNS` list in `make_fixture.py` and is repeated in `findings/panel.py` (Task 6).

- [x] **Step 1: Write the failing contract tests**

Create `tests/tools/test_contracts.py`:
```python
import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

C = Path("contracts")
SCHEMAS = ["panel", "projects", "findings", "models", "briefs", "model_card"]


def test_schemas_are_valid_json_schema():
    for name in SCHEMAS:
        schema = json.loads((C / f"{name}.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_enums_match_schemas():
    enums = json.loads((C / "enums.json").read_text(encoding="utf-8"))
    panel = json.loads((C / "panel.schema.json").read_text(encoding="utf-8"))
    assert panel["properties"]["snapshot"]["enum"] == enums["snapshot"]
    projects = json.loads((C / "projects.schema.json").read_text(encoding="utf-8"))
    assert projects["$defs"]["Flag"]["properties"]["type"]["enum"] == enums["finding_type"]
    assert projects["$defs"]["Flag"]["properties"]["severity"]["enum"] == enums["severity"]


def test_fixture_rows_validate_and_cover_every_snapshot():
    schema = json.loads((C / "panel.schema.json").read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    from tools.validate import csv_rows  # typed conversion shared with the gate
    rows = list(csv_rows(C / "fixtures" / "panel.sample.csv"))
    assert len(rows) == 52  # Dec 11, Apr 11, May 10, Jun 10, Jul 10
    for r in rows:
        assert list(v.iter_errors(r)) == []
    assert {r["snapshot"] for r in rows} == {"2025-12", "2026-04", "2026-05", "2026-06", "2026-07"}
    flags = {f for r in rows for f in r["parse_flags"].split(";") if f}
    assert {"NO_PMGID", "NO_LEGACY_CODE", "NO_PROJECT_CODE", "MULTILINE_STATE"} <= flags
```

Create `tests/tools/test_validate.py`:
```python
import os
import subprocess
import sys

import pytest


@pytest.mark.skipif(os.environ.get("AGRIM_IN_VALIDATE") == "1", reason="validate.py runs pytest itself; do not recurse")
def test_validator_exits_zero_on_clean_repo():
    p = subprocess.run([sys.executable, "tools/validate.py"], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "FAIL" not in p.stdout
```

- [x] **Step 2: Run them to verify they fail**

Run: `pytest tests/tools -q`
Expected: FAIL (files missing).

- [x] **Step 3: Write `contracts/enums.json` and `contracts/CHANGELOG.md`**

`contracts/enums.json`:
```json
{
  "snapshot": ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"],
  "finding_type": ["EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL", "DOC_PASSED", "DOC_UNREACHABLE", "DOC_REVISED_FILED", "COST_REVISED_FILED", "STAT_ANOMALY"],
  "severity": ["critical", "high", "medium", "low", "info"],
  "exit_partition": ["LAST_SEEN_GE_95", "LAST_SEEN_50_95", "LAST_SEEN_LT_50", "UNKNOWN"],
  "parse_flag": ["MULTILINE_STATE", "NO_PMGID", "NO_LEGACY_CODE", "NO_PROJECT_CODE", "NUM_PARSE_FAIL", "DATE_PARSE_FAIL", "ROW_SPANS_PAGE"],
  "model_id": ["LR_A", "HGB_A", "HGB_B", "HGB_B_SHUFFLED", "ZERO", "OWN_VELOCITY", "HGB", "OLS"],
  "pair_id": ["P1", "P2", "P3", "P4"],
  "band": ["red", "amber", "green"]
}
```

`contracts/CHANGELOG.md`:
```markdown
# Contract changelog
- 2026-09-06 v1.0.0 — initial schemas (panel, projects, findings, models, briefs, model_card), enums, fixture.
```

- [x] **Step 4: Write `contracts/panel.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PanelRow",
  "type": "object",
  "additionalProperties": false,
  "required": ["snapshot", "source_file", "source_sha256", "page", "sl_no", "project_code", "legacy_ocms_code", "pmgid", "project_name", "agency_raw", "table_section", "state", "approval_month", "start_month", "doc_original", "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct", "parse_flags"],
  "properties": {
    "snapshot": {"type": "string", "enum": ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]},
    "source_file": {"type": "string", "minLength": 1},
    "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "page": {"type": "integer", "minimum": 1},
    "sl_no": {"type": "integer", "minimum": 1},
    "project_code": {"type": ["string", "null"], "pattern": "^[0-9]{6}$"},
    "legacy_ocms_code": {"type": ["string", "null"], "minLength": 1},
    "pmgid": {"type": ["string", "null"], "minLength": 1},
    "project_name": {"type": "string", "minLength": 1},
    "agency_raw": {"type": ["string", "null"], "minLength": 1},
    "table_section": {"type": ["string", "null"], "minLength": 1},
    "state": {"type": ["string", "null"], "minLength": 1},
    "approval_month": {"type": ["string", "null"], "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])$"},
    "start_month": {"type": ["string", "null"], "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])$"},
    "doc_original": {"type": ["string", "null"], "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])$"},
    "doc_revised": {"type": ["string", "null"], "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])$"},
    "cost_original_cr": {"type": ["number", "null"], "minimum": 0},
    "cost_revised_cr": {"type": ["number", "null"], "minimum": 0},
    "expenditure_cum_cr": {"type": ["number", "null"], "minimum": 0},
    "physical_progress_pct": {"type": ["number", "null"], "minimum": 0},
    "parse_flags": {"type": "string", "pattern": "^$|^[A-Z_]+(;[A-Z_]+)*$"}
  }
}
```
(`physical_progress_pct` has no maximum on purpose: the PDF can print 101 and the `PROG_GT_100` finding must see it.)

- [x] **Step 5: Write `contracts/projects.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Projects",
  "type": "array",
  "items": {"$ref": "#/$defs/Project"},
  "$defs": {
    "Source": {"type": "object", "additionalProperties": false, "required": ["snapshot", "page"],
      "properties": {"snapshot": {"type": "string"}, "page": {"type": "integer"}}},
    "SnapshotRow": {"type": "object", "additionalProperties": false,
      "required": ["snapshot", "page", "doc_original", "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct"],
      "properties": {
        "snapshot": {"type": "string"}, "page": {"type": "integer"},
        "doc_original": {"type": ["string", "null"]}, "doc_revised": {"type": ["string", "null"]},
        "cost_original_cr": {"type": ["number", "null"]}, "cost_revised_cr": {"type": ["number", "null"]},
        "expenditure_cum_cr": {"type": ["number", "null"]}, "physical_progress_pct": {"type": ["number", "null"]}}},
    "Flag": {"type": "object", "additionalProperties": false,
      "required": ["type", "severity", "from_snapshot", "to_snapshot", "before", "after", "detail", "sources"],
      "properties": {
        "type": {"type": "string", "enum": ["EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL", "DOC_PASSED", "DOC_UNREACHABLE", "DOC_REVISED_FILED", "COST_REVISED_FILED", "STAT_ANOMALY"]},
        "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
        "from_snapshot": {"type": ["string", "null"]}, "to_snapshot": {"type": "string"},
        "before": {"type": ["number", "string", "null"]}, "after": {"type": ["number", "string", "null"]},
        "detail": {"type": "string"},
        "sources": {"type": "array", "items": {"$ref": "#/$defs/Source"}}}},
    "Factor": {"type": "object", "additionalProperties": false, "required": ["feature", "contribution", "value"],
      "properties": {"feature": {"type": "string"}, "contribution": {"type": "number"}, "value": {"type": ["number", "string", "null"]}}},
    "ML": {"type": "object", "additionalProperties": false,
      "required": ["slip_prob", "slip_rank", "slip_top_factors", "progress_next_pred", "expected_completion", "expected_delay_months", "peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months", "anomaly_score", "anomaly_flag", "scored_at_snapshot"],
      "properties": {
        "slip_prob": {"type": ["number", "null"]}, "slip_rank": {"type": ["integer", "null"]},
        "slip_top_factors": {"type": "array", "items": {"$ref": "#/$defs/Factor"}},
        "progress_next_pred": {"type": ["number", "null"]}, "expected_completion": {"type": ["string", "null"]},
        "expected_delay_months": {"type": ["number", "null"]},
        "peer_expected_cost_overrun_pct": {"type": ["number", "null"]}, "cost_overrun_residual_pct": {"type": ["number", "null"]},
        "peer_expected_time_overrun_months": {"type": ["number", "null"]}, "time_overrun_residual_months": {"type": ["number", "null"]},
        "anomaly_score": {"type": ["number", "null"]}, "anomaly_flag": {"type": "boolean"},
        "scored_at_snapshot": {"type": "string"}}},
    "Risk": {"type": "object", "additionalProperties": false, "required": ["score", "band", "reasons"],
      "properties": {"score": {"type": "number", "minimum": 0, "maximum": 100},
        "band": {"type": "string", "enum": ["red", "amber", "green"]},
        "reasons": {"type": "array", "items": {"type": "string"}}}},
    "Project": {"type": "object", "additionalProperties": false,
      "required": ["project_code", "project_name", "agency_raw", "state", "sector", "status", "first_seen", "last_seen", "snapshots", "flags", "risk", "ml"],
      "properties": {
        "project_code": {"type": "string"}, "project_name": {"type": "string"},
        "agency_raw": {"type": ["string", "null"]}, "state": {"type": ["string", "null"]}, "sector": {"type": ["string", "null"]},
        "status": {"type": "string", "enum": ["ongoing", "exited"]},
        "first_seen": {"type": "string"}, "last_seen": {"type": "string"},
        "snapshots": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/SnapshotRow"}},
        "flags": {"type": "array", "items": {"$ref": "#/$defs/Flag"}},
        "risk": {"$ref": "#/$defs/Risk"},
        "ml": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/ML"}]}}}
  }
}
```

- [x] **Step 6: Write `contracts/findings.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Findings",
  "type": "object",
  "additionalProperties": false,
  "required": ["meta", "contradictions", "exits", "early_warning", "field_audit", "disclosure_lag", "by_state", "by_sector", "review_pack", "assistant"],
  "$defs": {
    "Source": {"type": "object", "additionalProperties": false, "required": ["snapshot", "page"],
      "properties": {"snapshot": {"type": "string"}, "page": {"type": "integer"}}},
    "Sources": {"type": "array", "items": {"$ref": "#/$defs/Source"}},
    "Group": {"type": "object", "additionalProperties": false, "required": ["key", "projects", "flagged", "red"],
      "properties": {"key": {"type": "string"}, "projects": {"type": "integer"}, "flagged": {"type": "integer"}, "red": {"type": "integer"}}}
  },
  "properties": {
    "meta": {"type": "object", "additionalProperties": false,
      "required": ["contract_version", "generated_at", "snapshots", "coverage", "headline"],
      "properties": {
        "contract_version": {"type": "string"}, "generated_at": {"type": "string"},
        "snapshots": {"type": "array", "items": {"type": "string"}},
        "coverage": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["snapshot", "rows_parsed", "rows_printed", "pct"],
          "properties": {"snapshot": {"type": "string"}, "rows_parsed": {"type": "integer"}, "rows_printed": {"type": ["integer", "null"]}, "pct": {"type": ["number", "null"]}}}},
        "headline": {"type": "object", "additionalProperties": false,
          "required": ["projects_latest", "cost_revised_total_cr", "overrun_total_cr", "contradictions_total", "exits_total", "unreachable_total", "watchlist_size"],
          "properties": {"projects_latest": {"type": "integer"}, "cost_revised_total_cr": {"type": "number"}, "overrun_total_cr": {"type": "number"}, "contradictions_total": {"type": "integer"}, "exits_total": {"type": "integer"}, "unreachable_total": {"type": "integer"}, "watchlist_size": {"type": "integer"}}}}},
    "contradictions": {"type": "object", "additionalProperties": false, "required": ["by_type", "rows"],
      "properties": {
        "by_type": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["type", "count"],
          "properties": {"type": {"type": "string"}, "count": {"type": "integer"}}}},
        "rows": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["project_code", "project_name", "type", "severity", "from_snapshot", "to_snapshot", "before", "after", "detail", "sources"],
          "properties": {"project_code": {"type": "string"}, "project_name": {"type": "string"}, "type": {"type": "string"}, "severity": {"type": "string"},
            "from_snapshot": {"type": ["string", "null"]}, "to_snapshot": {"type": "string"},
            "before": {"type": ["number", "string", "null"]}, "after": {"type": ["number", "string", "null"]}, "detail": {"type": "string"}, "sources": {"$ref": "#/$defs/Sources"}}}}}},
    "exits": {"type": "object", "additionalProperties": false, "required": ["pairs", "rows"],
      "properties": {
        "pairs": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["from", "to", "exited", "entered", "exited_cost_revised_cr", "commissioned_printed"],
          "properties": {"from": {"type": "string"}, "to": {"type": "string"}, "exited": {"type": "integer"}, "entered": {"type": "integer"}, "exited_cost_revised_cr": {"type": "number"}, "commissioned_printed": {"type": ["integer", "null"]}}}},
        "rows": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["project_code", "project_name", "last_seen", "last_progress_pct", "last_expenditure_cr", "last_cost_revised_cr", "partition", "sources"],
          "properties": {"project_code": {"type": "string"}, "project_name": {"type": "string"}, "last_seen": {"type": "string"}, "last_progress_pct": {"type": ["number", "null"]}, "last_expenditure_cr": {"type": ["number", "null"]}, "last_cost_revised_cr": {"type": ["number", "null"]},
            "partition": {"type": "string", "enum": ["LAST_SEEN_GE_95", "LAST_SEEN_50_95", "LAST_SEEN_LT_50", "UNKNOWN"]}, "sources": {"$ref": "#/$defs/Sources"}}}}}},
    "early_warning": {"type": "object", "additionalProperties": false, "required": ["rows"],
      "properties": {"rows": {"type": "array", "items": {"type": "object", "additionalProperties": false,
        "required": ["project_code", "project_name", "velocity_pct_per_month", "months_needed", "months_remaining", "ratio", "severity", "sources"],
        "properties": {"project_code": {"type": "string"}, "project_name": {"type": "string"}, "velocity_pct_per_month": {"type": ["number", "null"]}, "months_needed": {"type": ["number", "null"]}, "months_remaining": {"type": "integer"}, "ratio": {"type": ["number", "null"]}, "severity": {"type": "string"}, "sources": {"$ref": "#/$defs/Sources"}}}}}},
    "field_audit": {"type": "object", "additionalProperties": false,
      "required": ["snapshot", "terminal_digit", "whole_number_share", "multiple_of_5_share", "multiple_of_10_share", "staleness_by_agency"],
      "properties": {"snapshot": {"type": "string"},
        "terminal_digit": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["digit", "count", "share"],
          "properties": {"digit": {"type": "integer"}, "count": {"type": "integer"}, "share": {"type": "number"}}}},
        "whole_number_share": {"type": "number"}, "multiple_of_5_share": {"type": "number"}, "multiple_of_10_share": {"type": "number"},
        "staleness_by_agency": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["agency_raw", "projects", "share_unchanged"],
          "properties": {"agency_raw": {"type": "string"}, "projects": {"type": "integer"}, "share_unchanged": {"type": "number"}}}}}},
    "disclosure_lag": {"type": "object", "additionalProperties": false, "required": ["status", "median_lag_months", "rows"],
      "properties": {"status": {"type": "string", "enum": ["computed", "not_computed"]}, "median_lag_months": {"type": ["number", "null"]},
        "rows": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["project_code", "filed_at", "first_unreachable", "lag_months"],
          "properties": {"project_code": {"type": "string"}, "filed_at": {"type": "string"}, "first_unreachable": {"type": ["string", "null"]}, "lag_months": {"type": ["integer", "null"]}}}}}},
    "by_state": {"type": "array", "items": {"$ref": "#/$defs/Group"}},
    "by_sector": {"type": "array", "items": {"$ref": "#/$defs/Group"}},
    "review_pack": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "required": ["project_code", "project_name", "state", "sector", "risk_band", "risk_score", "slip_prob", "expected_delay_months", "flag_types", "page"],
      "properties": {"project_code": {"type": "string"}, "project_name": {"type": "string"}, "state": {"type": ["string", "null"]}, "sector": {"type": ["string", "null"]}, "risk_band": {"type": "string"}, "risk_score": {"type": "number"}, "slip_prob": {"type": ["number", "null"]}, "expected_delay_months": {"type": ["number", "null"]}, "flag_types": {"type": "string"}, "page": {"type": "integer"}}}},
    "assistant": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["id", "question", "answer", "sources"],
      "properties": {"id": {"type": "integer"}, "question": {"type": "string"}, "answer": {"type": "string"}, "sources": {"$ref": "#/$defs/Sources"}}}}
  }
}
```

- [x] **Step 7: Write `contracts/models.schema.json`, `contracts/briefs.schema.json`, `contracts/model_card.schema.json`**

`contracts/models.schema.json`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Models",
  "type": "object",
  "additionalProperties": false,
  "required": ["meta", "m1_slip", "m2_progress", "m3_drivers", "m4_anomaly"],
  "$defs": {
    "Point": {"type": "object", "additionalProperties": false, "required": ["x", "y"], "properties": {"x": {"type": "number"}, "y": {"type": "number"}}},
    "Named": {"type": "object", "additionalProperties": false, "required": ["feature", "value"], "properties": {"feature": {"type": "string"}, "value": {"type": "number"}}}
  },
  "properties": {
    "meta": {"type": "object", "additionalProperties": false,
      "required": ["contract_version", "generated_at", "sklearn_version", "random_state", "omp_threads", "pairs", "test_pair", "train_pairs"],
      "properties": {"contract_version": {"type": "string"}, "generated_at": {"type": "string"}, "sklearn_version": {"type": "string"}, "random_state": {"type": "integer"}, "omp_threads": {"type": "integer"},
        "pairs": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["id", "from", "to", "gap_months", "n", "positives", "censored_exits"],
          "properties": {"id": {"type": "string"}, "from": {"type": "string"}, "to": {"type": "string"}, "gap_months": {"type": "integer"}, "n": {"type": "integer"}, "positives": {"type": "integer"}, "censored_exits": {"type": "integer"}}}},
        "test_pair": {"type": "string"}, "train_pairs": {"type": "array", "items": {"type": "string"}}}},
    "m1_slip": {"type": "object", "additionalProperties": false, "required": ["feature_sets", "results", "importance_HGB_B", "coefficients_LR_A", "watchlist"],
      "properties": {
        "feature_sets": {"type": "object", "additionalProperties": false, "required": ["A", "B"], "properties": {"A": {"type": "array", "items": {"type": "string"}}, "B": {"type": "array", "items": {"type": "string"}}}},
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["model_id", "test_pair", "n", "positives", "base_rate", "pr_auc", "roc_auc", "precision_at_100", "recall_at_100", "lift_at_100", "calibration", "pr_curve"],
          "properties": {"model_id": {"type": "string"}, "test_pair": {"type": "string"}, "n": {"type": "integer"}, "positives": {"type": "integer"}, "base_rate": {"type": "number"}, "pr_auc": {"type": "number"}, "roc_auc": {"type": ["number", "null"]}, "precision_at_100": {"type": "number"}, "recall_at_100": {"type": "number"}, "lift_at_100": {"type": ["number", "null"]},
            "calibration": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["bin", "mean_pred", "mean_obs", "n"], "properties": {"bin": {"type": "integer"}, "mean_pred": {"type": ["number", "null"]}, "mean_obs": {"type": ["number", "null"]}, "n": {"type": "integer"}}}},
            "pr_curve": {"type": "array", "items": {"$ref": "#/$defs/Point"}}}}},
        "importance_HGB_B": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["feature", "mean", "std"], "properties": {"feature": {"type": "string"}, "mean": {"type": "number"}, "std": {"type": "number"}}}},
        "coefficients_LR_A": {"type": "array", "items": {"$ref": "#/$defs/Named"}},
        "watchlist": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["project_code", "slip_prob", "slip_rank"], "properties": {"project_code": {"type": "string"}, "slip_prob": {"type": "number"}, "slip_rank": {"type": "integer"}}}}}},
    "m2_progress": {"type": "object", "additionalProperties": false, "required": ["results", "winner", "agreement_with_F3"],
      "properties": {
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["model_id", "test_pair", "n", "mae", "median_ae"], "properties": {"model_id": {"type": "string"}, "test_pair": {"type": "string"}, "n": {"type": "integer"}, "mae": {"type": "number"}, "median_ae": {"type": "number"}}}},
        "winner": {"type": "string"},
        "agreement_with_F3": {"type": "object", "additionalProperties": false, "required": ["n", "share_same_direction"], "properties": {"n": {"type": "integer"}, "share_same_direction": {"type": ["number", "null"]}}}}},
    "m3_drivers": {"type": "object", "additionalProperties": false, "required": ["snapshot", "n", "results", "partial_dependence", "sector_effects", "coefficients_OLS"],
      "properties": {"snapshot": {"type": "string"}, "n": {"type": "integer"},
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["target", "model_id", "cv_r2", "cv_mae"], "properties": {"target": {"type": "string"}, "model_id": {"type": "string"}, "cv_r2": {"type": "number"}, "cv_mae": {"type": "number"}}}},
        "partial_dependence": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["target", "feature", "grid", "values"], "properties": {"target": {"type": "string"}, "feature": {"type": "string"}, "grid": {"type": "array", "items": {"type": "number"}}, "values": {"type": "array", "items": {"type": "number"}}}}},
        "sector_effects": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["sector", "effect_cost_pct", "effect_time_months", "n"], "properties": {"sector": {"type": "string"}, "effect_cost_pct": {"type": "number"}, "effect_time_months": {"type": "number"}, "n": {"type": "integer"}}}},
        "coefficients_OLS": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["target", "feature", "coef"], "properties": {"target": {"type": "string"}, "feature": {"type": "string"}, "coef": {"type": "number"}}}}}},
    "m4_anomaly": {"type": "object", "additionalProperties": false, "required": ["n", "contamination", "flagged"],
      "properties": {"n": {"type": "integer"}, "contamination": {"type": "string"},
        "flagged": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["project_code", "pair", "score", "sources"],
          "properties": {"project_code": {"type": "string"}, "pair": {"type": "string"}, "score": {"type": "number"}, "sources": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["snapshot", "page"], "properties": {"snapshot": {"type": "string"}, "page": {"type": "integer"}}}}}}}}}
  }
}
```

`contracts/briefs.schema.json`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Briefs",
  "type": "array",
  "items": {"type": "object", "additionalProperties": false,
    "required": ["project_code", "brief", "model", "seed", "generated_at", "grounded", "attempts", "facts_hash"],
    "properties": {"project_code": {"type": "string"}, "brief": {"type": "string", "minLength": 1}, "model": {"type": "string"}, "seed": {"type": "integer"}, "generated_at": {"type": "string"}, "grounded": {"type": "boolean"}, "attempts": {"type": "integer"}, "facts_hash": {"type": "string"}}}
}
```

`contracts/model_card.schema.json`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ModelCard",
  "type": "object",
  "additionalProperties": false,
  "required": ["generated_at", "sections"],
  "properties": {"generated_at": {"type": "string"},
    "sections": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["title", "lines"],
      "properties": {"title": {"type": "string"}, "lines": {"type": "array", "items": {"type": "string"}}}}}}
}
```

- [x] **Step 8: Write the fixture generator and generate the fixture**

Create `contracts/fixtures/make_fixture.py`:
```python
"""Writes contracts/fixtures/panel.sample.csv: 12 projects x 5 snapshots, every event class the findings must detect.
Run: python contracts/fixtures/make_fixture.py
"""
import csv
import hashlib
from pathlib import Path

SNAPS = ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
COLUMNS = ["snapshot", "source_file", "source_sha256", "page", "sl_no", "project_code", "legacy_ocms_code", "pmgid",
           "project_name", "agency_raw", "table_section", "state", "approval_month", "start_month", "doc_original",
           "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct", "parse_flags"]

# series: snapshot -> (doc_revised, cost_revised, expenditure, progress); None entries = not present that month
P = [
    dict(code="100001", name="Clean Road Corridor Phase I", agency="NHAI", section="Road Transport and Highways", state="Gujarat",
         approval="2023-02", start="2023-06", doc_o="2029-06", cost_o=500.0,
         series={"2025-12": (None, 520.0, 100.0, 20.0), "2026-04": (None, 520.0, 130.0, 28.0), "2026-05": (None, 520.0, 150.0, 31.0),
                 "2026-06": (None, 520.0, 170.0, 34.0), "2026-07": (None, 520.0, 190.0, 37.0)}),
    dict(code="100002", name="Hydro Power Station Unit 2", agency="NHPC", section="Power", state="Himachal Pradesh",
         approval="2020-08", start="2021-01", doc_o="2026-12", cost_o=900.0,
         series={"2025-12": (None, 950.0, 500.0, 60.0), "2026-04": (None, 950.0, 620.0, 64.0), "2026-05": (None, 950.0, 120.0, 66.0),
                 "2026-06": (None, 950.0, 140.0, 68.0), "2026-07": (None, 950.0, 160.0, 70.0)}),
    dict(code="100003", name="Doubling of Rail Line Section B", agency="Railways", section="Railways", state="Bihar",
         approval="2022-03", start="2022-09", doc_o="2027-03", cost_o=700.0,
         series={"2025-12": (None, 700.0, 200.0, 30.0), "2026-04": (None, 700.0, 240.0, 38.0), "2026-05": (None, 700.0, 260.0, 40.0),
                 "2026-06": (None, 700.0, 280.0, 35.0), "2026-07": (None, 700.0, 300.0, 41.0)}),
    dict(code="100004", name="Refinery Expansion", agency="IOCL", section="Petroleum", state="Odisha",
         approval="2021-05", start="2021-10", doc_o="2026-10", cost_o=1000.0,
         series={"2025-12": (None, 1000.0, 700.0, 70.0), "2026-04": (None, 1000.0, 850.0, 78.0), "2026-05": (None, 1000.0, 950.0, 84.0),
                 "2026-06": (None, 1000.0, 1200.0, 90.0), "2026-07": (None, 1000.0, 1250.0, 92.0)}),
    dict(code="100005", name="Stalled Bridge Works", agency="NHAI", section="Road Transport and Highways", state="Assam",
         approval="2019-04", start="2019-09", doc_o="2025-06", cost_o=300.0,
         series={s: (None, 300.0, 30.0, 0.0) for s in SNAPS}),
    dict(code="100006", name="Slow Metro Extension", agency="DMRC", section="Urban Development", state="Delhi",
         approval="2021-11", start="2022-02", doc_o="2026-06", cost_o=400.0,
         series={"2025-12": ("2026-12", 450.0, 210.0, 50.0), "2026-04": ("2026-12", 450.0, 220.0, 52.0), "2026-05": ("2027-06", 450.0, 225.0, 53.0),
                 "2026-06": ("2027-06", 450.0, 230.0, 54.0), "2026-07": ("2027-06", 450.0, 235.0, 55.0)}),
    dict(code="100007", name="Nearly Done Port Berth", agency="Port Authority", section="Shipping and Ports", state="Tamil Nadu",
         approval="2020-01", start="2020-06", doc_o="2026-03", cost_o=600.0,
         series={"2025-12": (None, 640.0, 570.0, 90.0), "2026-04": (None, 640.0, 600.0, 95.0), "2026-05": (None, 640.0, 615.0, 97.0)}),
    dict(code="100008", name="Vanishing Pipeline Segment", agency="GAIL", section="Petroleum", state="Rajasthan",
         approval="2022-07", start="2022-12", doc_o="2027-12", cost_o=800.0,
         series={"2025-12": (None, 800.0, 250.0, 35.0), "2026-04": (None, 800.0, 300.0, 40.0)}),
    dict(code="100009", name="New Coal Handling Plant", agency="Coal India", section="Coal", state="Jharkhand",
         approval="2026-01", start="2026-04", doc_o="2029-03", cost_o=450.0,
         series={"2026-06": (None, 450.0, 20.0, 5.0), "2026-07": (None, 450.0, 40.0, 9.0)}),
    dict(code="100010", name="Cost Revised Steel Plant", agency="SAIL", section="Steel", state="Chhattisgarh",
         approval="2021-09", start="2022-01", doc_o="2027-09", cost_o=800.0,
         series={"2025-12": (None, 800.0, 300.0, 45.0), "2026-04": (None, 800.0, 340.0, 50.0), "2026-05": (None, 800.0, 380.0, 55.0),
                 "2026-06": (None, 800.0, 420.0, 60.0), "2026-07": (None, 1600.0, 460.0, 65.0)}),
    dict(code="100011", name="Overreported Airport Terminal", agency="AAI", section="Civil Aviation", state="Kerala",
         approval="2021-03", start="2021-06", doc_o="2020-01", cost_o=350.0,
         series={"2025-12": (None, 360.0, 330.0, 95.0), "2026-04": (None, 360.0, 340.0, 97.0), "2026-05": (None, 360.0, 345.0, 98.0),
                 "2026-06": (None, 360.0, 350.0, 99.0), "2026-07": (None, 360.0, 355.0, 101.0)}),
    dict(code="100012", name="Island Jetty Works", agency="Port Authority", section="Shipping and Ports", state="Andaman and Nicobar Islands",
         approval="2023-08", start="2024-01", doc_o="2027-01", cost_o=250.0,
         series={"2025-12": (None, 250.0, 40.0, 12.0), "2026-04": (None, 250.0, 60.0, 18.0), "2026-05": (None, 250.0, 70.0, 21.0),
                 "2026-06": (None, 250.0, 80.0, 24.0), "2026-07": (None, 250.0, 90.0, 27.0)}),
]


def rows():
    for s_i, snap in enumerate(SNAPS):
        fname = f"fixture_{snap}.pdf"
        sha = hashlib.sha256(fname.encode()).hexdigest()
        sl = 0
        for p in P:
            if snap not in p["series"]:
                continue
            sl += 1
            doc_r, cost_r, exp, prog = p["series"][snap]
            dec = snap == "2025-12"
            flags = []
            code = p["code"]
            if dec:
                flags += ["NO_PMGID", "NO_LEGACY_CODE"]
            if dec and code == "100012":
                code = None
                flags.append("NO_PROJECT_CODE")
            if snap == "2026-04" and p["code"] == "100012":
                flags.append("MULTILINE_STATE")
            yield {
                "snapshot": snap, "source_file": fname, "source_sha256": sha, "page": 55 + s_i, "sl_no": sl,
                "project_code": code, "legacy_ocms_code": None if dec else f"N0400{p['code'][2:]}", "pmgid": None if dec else f"PMG{p['code']}",
                "project_name": p["name"], "agency_raw": p["agency"], "table_section": p["section"], "state": p["state"],
                "approval_month": p["approval"], "start_month": p["start"], "doc_original": p["doc_o"], "doc_revised": doc_r,
                "cost_original_cr": p["cost_o"], "cost_revised_cr": cost_r, "expenditure_cum_cr": exp, "physical_progress_pct": prog,
                "parse_flags": ";".join(flags),
            }


def write(path=Path("contracts/fixtures/panel.sample.csv")):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows():
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return path


if __name__ == "__main__":
    print("wrote", write())
```

Run: `python contracts/fixtures/make_fixture.py`
Expected: `wrote contracts\fixtures\panel.sample.csv`; the file has 53 lines (header + 52 rows: Dec 11, Apr 11, May 10, Jun 10, Jul 10 — 100009 enters in June, 100008 leaves after April, 100007 leaves after May).

- [x] **Step 9: Write the synthetic panel generator (used by model tests in Tasks 10–14)**

Create `contracts/fixtures/synthetic_panel.py`:
```python
"""Deterministic synthetic panel with a planted slip signal, for model tests. Never used for real findings.
Usage: from contracts.fixtures.synthetic_panel import write; write(Path('data/out/tmp_synth.csv'), n_projects=600, seed=0)
"""
import csv
import hashlib
from pathlib import Path

import numpy as np

SNAPS = ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
GAPS = {"2025-12": 0, "2026-04": 4, "2026-05": 5, "2026-06": 6, "2026-07": 7}  # months since Dec 2025
SECTORS = ["Railways", "Road Transport and Highways", "Power", "Petroleum", "Coal", "Urban Development"]
STATES = ["Gujarat", "Bihar", "Odisha", "Assam", "Delhi", "Tamil Nadu", "Rajasthan", "Jharkhand", "Kerala", "Maharashtra"]
COLUMNS = ["snapshot", "source_file", "source_sha256", "page", "sl_no", "project_code", "legacy_ocms_code", "pmgid",
           "project_name", "agency_raw", "table_section", "state", "approval_month", "start_month", "doc_original",
           "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct", "parse_flags"]


def _ym(year, month):
    return f"{year:04d}-{month:02d}"


def _add_months(ym, k):
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) + k
    return _ym(t // 12, t % 12 + 1)


def write(path, n_projects=600, seed=0):
    rng = np.random.RandomState(seed)
    rows = []
    for i in range(n_projects):
        code = f"{200000 + i:06d}"
        sector = SECTORS[rng.randint(len(SECTORS))]
        state = STATES[rng.randint(len(STATES))]
        agency = f"{sector[:4].upper()}-AG{rng.randint(6)}"
        appr_year = rng.randint(2015, 2025)
        approval = _ym(appr_year, rng.randint(1, 13))
        planned = int(rng.randint(24, 84))
        doc_o = _add_months(approval, planned)
        cost_o = float(np.round(np.exp(rng.normal(6.5, 0.8)), 2))
        cost_r = float(np.round(cost_o * (1 + max(0.0, rng.normal(0.08, 0.15))), 2))
        prog = float(np.clip(rng.uniform(0, 90), 0, 100))
        vel = float(np.clip(rng.normal(1.6 + 0.4 * SECTORS.index(sector) / 5, 0.7), 0.05, 4.0))
        doc_r = None
        present_from = 0 if rng.rand() > 0.05 else 3  # 5% enter late
        exited = False
        for s_i, snap in enumerate(SNAPS):
            if s_i < present_from or exited:
                continue
            if s_i > 0:
                gap = GAPS[snap] - GAPS[SNAPS[s_i - 1]]
                prog = float(min(100.0, prog + vel * gap + rng.normal(0, 0.8 * gap)))
                if rng.rand() < 0.01:
                    prog = max(0.0, prog - 6.0)  # planted PROG_DECREASE
                # planted slip signal: unreachable pace => higher chance of filing a revised DoC
                doc_cur = doc_r or doc_o
                rem = (int(doc_cur[:4]) * 12 + int(doc_cur[5:7])) - (int(snap[:4]) * 12 + int(snap[5:7]))
                need = (100 - prog) / max(vel, 0.05)
                ratio = need / max(rem, 0.5) if rem > 0 else 9.0
                p_slip = 1 / (1 + np.exp(-(-2.2 + 1.1 * np.log1p(max(ratio, 0)) + 0.3 * (sector == "Railways"))))
                if prog < 100 and rng.rand() < p_slip:
                    doc_r = _add_months(doc_cur, int(rng.randint(3, 13)))
                if rng.rand() < 0.02:
                    exited = True
                    continue
            exp = float(np.round(cost_r * prog / 100 * rng.uniform(0.85, 1.05), 2))
            if s_i > 0 and rng.rand() < 0.01:
                exp = float(np.round(exp * 0.2, 2))  # planted EXP_DECREASE
            rows.append({"snapshot": snap, "source_file": f"synthetic_{snap}.pdf", "source_sha256": hashlib.sha256(snap.encode()).hexdigest(),
                         "page": 55 + (i // 15), "sl_no": i + 1, "project_code": code, "legacy_ocms_code": f"N{code}00",
                         "pmgid": f"PMG{code}", "project_name": f"Synthetic Project {code}", "agency_raw": agency,
                         "table_section": sector, "state": state, "approval_month": approval, "start_month": _add_months(approval, 3),
                         "doc_original": doc_o, "doc_revised": doc_r, "cost_original_cr": cost_o, "cost_revised_cr": cost_r,
                         "expenditure_cum_cr": max(exp, 0.0), "physical_progress_pct": round(prog, 2), "parse_flags": ""})
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    order = {s: k for k, s in enumerate(SNAPS)}
    rows.sort(key=lambda r: (order[r["snapshot"]], r["sl_no"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return path
```

- [x] **Step 10: Write `tools/validate.py` (the gate; later tasks never modify it)**

```python
#!/usr/bin/env python
"""THE gate. Exit 0 = everything that exists is valid. A step SKIPs (does not fail) when its inputs do not exist yet."""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "contracts"
DATA = ROOT / "web" / "public" / "data"
FAILS = []

NUM = {"cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct"}
INT = {"page", "sl_no"}


def fail(msg):
    FAILS.append(msg)
    print("FAIL", msg)


def ok(msg):
    print("ok  ", msg)


def skip(msg):
    print("SKIP", msg)


def schema(name):
    s = json.loads((C / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(s)
    return Draft202012Validator(s)


def csv_rows(path):
    """Yield typed dicts from a panel CSV: '' -> None (except parse_flags), numbers -> float/int."""
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row = {}
            for k, v in r.items():
                if v == "" and k != "parse_flags":
                    row[k] = None
                elif k in NUM:
                    try:
                        row[k] = float(v)
                    except ValueError:
                        row[k] = v
                elif k in INT:
                    try:
                        row[k] = int(v)
                    except ValueError:
                        row[k] = v
                else:
                    row[k] = v
            yield row


def step_schemas():
    enums = json.loads((C / "enums.json").read_text(encoding="utf-8"))
    for n in ["panel", "projects", "findings", "models", "briefs", "model_card"]:
        schema(n)
    p = json.loads((C / "projects.schema.json").read_text(encoding="utf-8"))
    if p["$defs"]["Flag"]["properties"]["type"]["enum"] != enums["finding_type"]:
        fail("enums.json finding_type differs from projects.schema.json")
    ok("schemas well-formed, enums consistent")


def step_panel(path, label):
    if not path.exists():
        return skip(f"{label}: {path.relative_to(ROOT)} missing")
    v = schema("panel")
    enums = json.loads((C / "enums.json").read_text(encoding="utf-8"))
    n = bad = 0
    for i, row in enumerate(csv_rows(path), start=2):
        n += 1
        errs = list(v.iter_errors(row))
        if errs:
            bad += 1
            if bad <= 5:
                fail(f"{label} line {i}: {errs[0].message}")
        for fl in row["parse_flags"].split(";"):
            if fl and fl not in enums["parse_flag"]:
                fail(f"{label} line {i}: unknown parse_flag {fl}")
    if bad == 0:
        ok(f"{label}: {n} rows valid")


def step_json(path, name):
    if not path.exists():
        return skip(f"{name}: {path.relative_to(ROOT)} missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    errs = list(schema(name).iter_errors(data))
    if errs:
        fail(f"{name}: {errs[0].json_path}: {errs[0].message}")
    else:
        ok(f"{name}: valid")


def run_findings(out):
    env = dict(os.environ, AGRIM_GENERATED_AT="fixture", OMP_NUM_THREADS="1")
    p = subprocess.run([sys.executable, "-m", "findings.run", "--panel", str(C / "fixtures" / "panel.sample.csv"),
                        "--out", str(out), "--no-models"], capture_output=True, text=True, env=env, cwd=ROOT)
    if p.returncode != 0:
        fail("findings.run on fixture failed:\n" + p.stdout[-2000:] + p.stderr[-2000:])
        return False
    return True


def step_determinism_and_golden():
    if not (ROOT / "findings" / "run.py").exists():
        return skip("findings/run.py missing: determinism + golden skipped")
    t1, t2 = ROOT / "data" / "out" / "tmp_run1", ROOT / "data" / "out" / "tmp_run2"
    for t in (t1, t2):
        shutil.rmtree(t, ignore_errors=True)
        t.mkdir(parents=True)
    if not (run_findings(t1) and run_findings(t2)):
        return
    for name in ["projects.json", "findings.json"]:
        if (t1 / name).read_bytes() != (t2 / name).read_bytes():
            fail(f"non-deterministic: {name} differs between two fixture runs")
        golden = C / "fixtures" / name.replace(".json", ".sample.json")
        if golden.exists():
            if golden.read_bytes() != (t1 / name).read_bytes():
                fail(f"golden mismatch: {golden.name} (regenerate only if the change is intended; log it in contracts/CHANGELOG.md)")
            else:
                ok(f"golden {golden.name} matches")
        else:
            skip(f"golden {golden.name} not yet committed")
    ok("fixture run deterministic")


def step_pytest():
    if not (ROOT / "tests").exists():
        return skip("tests/ missing")
    env = dict(os.environ, AGRIM_IN_VALIDATE="1")  # tests/tools/test_validate.py skips itself under this flag (no recursion)
    p = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True, cwd=ROOT, env=env)
    tail = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    if p.returncode != 0:
        fail("pytest failed: " + tail + "\n" + p.stdout[-3000:])
    else:
        ok("pytest: " + tail)


LITERAL = re.compile(r"(?<![\w.#-])\d{3,}(?![\w.])")
ALLOW = [re.compile(r"\b(19|20)\d{2}\b"), re.compile(r"\d+px"), re.compile(r"#[0-9a-fA-F]{3,8}"), re.compile(r"\d{3,}ms"),
         re.compile(r"localhost:\d+"), re.compile(r"\d{3,}/"), re.compile(r"e\d{3,}"), re.compile(r"\b(100|1000|200|404)\b")]
# 100/1000 are arithmetic constants and 200/404 are HTTP status codes, not data. Every other 3+ digit literal in web/src must come from JSON.


def step_literals():
    targets = list((ROOT / "web" / "src").rglob("*.ts")) + list((ROOT / "web" / "src").rglob("*.tsx"))
    pitch = ROOT / "deck" / "pitch.md"
    if pitch.exists():
        targets.append(pitch)
    if not targets:
        return skip("no web/src or deck/pitch.md yet")
    hits = 0
    for f in targets:
        for ln, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if line.lstrip().startswith("//") or line.lstrip().startswith("*"):
                continue
            stripped = line
            for a in ALLOW:
                stripped = a.sub("", stripped)
            if LITERAL.search(stripped):
                hits += 1
                if hits <= 10:
                    fail(f"hardcoded number in {f.relative_to(ROOT)}:{ln}: {line.strip()[:100]}")
    if hits == 0:
        ok(f"no hardcoded numbers in {len(targets)} files")


def _leaves(x, acc):
    if isinstance(x, dict):
        for v in x.values():
            _leaves(v, acc)
    elif isinstance(x, list):
        for v in x:
            _leaves(v, acc)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        acc.add(round(float(x), 4))
    elif isinstance(x, str):
        acc.add(x)


def step_deck_numbers():
    nums = ROOT / "deck" / "numbers.json"
    if not nums.exists():
        return skip("deck/numbers.json missing")
    acc = set()
    for name in ["findings.json", "models.json"]:
        if (DATA / name).exists():
            _leaves(json.loads((DATA / name).read_text(encoding="utf-8")), acc)
    missing = [k for k, v in json.loads(nums.read_text(encoding="utf-8")).items()
               if (round(float(v), 4) if isinstance(v, (int, float)) else v) not in acc]
    if missing:
        fail("deck/numbers.json values not found in findings/models JSON: " + ", ".join(missing[:10]))
    else:
        ok("deck/numbers.json all traceable")


def main():
    step_schemas()
    step_panel(C / "fixtures" / "panel.sample.csv", "fixture panel")
    step_panel(ROOT / "data" / "out" / "panel.csv", "data/out/panel.csv")
    for name, fn in [("projects", "projects.json"), ("findings", "findings.json"), ("models", "models.json"),
                     ("briefs", "briefs.json"), ("model_card", "model_card.json")]:
        step_json(DATA / fn, name)
    step_determinism_and_golden()
    step_pytest()
    step_literals()
    step_deck_numbers()
    print("=" * 60)
    print("RESULT:", "FAIL" if FAILS else "PASS", f"({len(FAILS)} failures)")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
```

- [x] **Step 11: Run the tests and the gate**

Run: `pytest -q`
Expected: all pass (the validator's own pytest step runs inside `test_validate` — that is fine, it is fast).

Run: `python tools/validate.py`
Expected: `RESULT: PASS`, with SKIP lines for panel.csv, JSON outputs, findings/run.py, web/src, deck.

- [x] **Step 12: Commit and open the PR**

```powershell
git switch -c task/02-contracts
git add -A
git commit -m "task 02: contracts, enums, fixtures, synthetic generator, validator gate"
git push -u origin task/02-contracts
gh pr create --title "Task 02: contracts and validator" --body "validate.py: PASS; pytest: passed"
```

---

### Task 3: Fetch the five PDFs, pin checksums, record the printed aggregates

**Files:**
- Create: `tools/fetch_pdfs.py`, `tools/show_page.py`, `data/pdfs/SHA256SUMS` (generated), `data/pdfs/*.pdf` (downloaded, committed), `data/aggregates.json`, `docs/DAY1-CHECKS.md`
- Test: `tests/tools/test_fetch.py`

**Interfaces:**
- Consumes: Task 2 validator.
- Produces: `data/pdfs/<file>` for each snapshot, `SHA256SUMS` (`<sha256>  <file>` per line); `data/aggregates.json` = `{snapshot: {"rows_printed": int, "cost_original_cr": number, "cost_revised_cr": number, "expenditure_cum_cr": number, "commissioned": int|null} | null}` read by Task 5 and Task 9; `tools.fetch_pdfs.PDFS` = `{snapshot: (file_name, url, expected_size)}` read by Task 4's adapters.

- [x] **Step 1: Write the failing checksum test (no network)**

Create `tests/tools/test_fetch.py`:
```python
import hashlib
from pathlib import Path

import pytest

from tools import fetch_pdfs as fp


def test_pdfs_table_has_all_snapshots():
    assert list(fp.PDFS) == ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
    for snap, (name, url, size) in fp.PDFS.items():
        assert name.endswith(".pdf") and url.startswith("https://www.mospi.gov.in/") and size > 6_000_000


def test_sums_roundtrip(tmp_path):
    f = tmp_path / "a.pdf"
    f.write_bytes(b"hello")
    sums = tmp_path / "SHA256SUMS"
    fp.write_sums([f], sums)
    assert sums.read_text().strip() == hashlib.sha256(b"hello").hexdigest() + "  a.pdf"
    assert fp.verify_sums(sums, tmp_path) == []
    f.write_bytes(b"tampered")
    assert fp.verify_sums(sums, tmp_path) == ["a.pdf"]


@pytest.mark.skipif(not Path("data/pdfs/SHA256SUMS").exists(), reason="PDFs not fetched yet")
def test_committed_pdfs_match_sums_and_sizes():
    assert fp.verify_sums(Path("data/pdfs/SHA256SUMS"), Path("data/pdfs")) == []
    for snap, (name, url, size) in fp.PDFS.items():
        assert (Path("data/pdfs") / name).stat().st_size == size, f"{name} size changed; re-fetch or update PDFS"
```

- [x] **Step 2: Run it to verify it fails**

Run: `pytest tests/tools/test_fetch.py -q`
Expected: FAIL with `No module named 'tools.fetch_pdfs'`.

- [x] **Step 3: Write `tools/fetch_pdfs.py` and `tools/show_page.py`**

`tools/fetch_pdfs.py`:
```python
"""Download the five Flash Report PDFs ONCE, verify sizes, write SHA256SUMS. The only network code in the parser side.
Run: python tools/fetch_pdfs.py            (downloads what is missing, then verifies)
     python tools/fetch_pdfs.py --verify   (verifies only)
"""
import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

M = "https://www.mospi.gov.in/uploads/publications_reports/"
PDFS = {
    "2025-12": ("FlashReport_December_2025.pdf", M + "publications_reports1769671627281_5812a634-546b-405d-921c-f84c4da453dc_FlashReport_December_2025.pdf", 6398361),
    "2026-04": ("Flash_Report_April_2026.pdf", M + "publications_reports1779688125413_332125c5-1fb9-4d23-87ca-dd89fc14cd15_Flash_Report_April_2026.pdf", 6543938),
    "2026-05": ("FlashReport_May_2026.pdf", M + "publications_reports1782388627305_2544b8eb-3ea2-40eb-ab6e-b150c40c4a9e_FlashReport_May_2026.pdf", 6460757),
    "2026-06": ("FlashReport_June_2026.pdf", M + "publications_reports1785229543014_f9b01e19-0a7a-4975-9276-34e02259c2e0_FlashReport_June_2026_.pdf", 6540236),
    "2026-07": ("FlashReport_July_2026.pdf", M + "publications_reports1787656864174_db1695c9-b038-4c20-964f-8cf5f2cdda5f_FlashReport_July_2026_.pdf", 6451056),
}
DIR = Path(__file__).resolve().parents[1] / "data" / "pdfs"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AGRIM fetch; student project)"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            out.write(chunk)


def write_sums(files, sums_path):
    lines = [f"{sha256(f)}  {Path(f).name}" for f in files]
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_sums(sums_path, directory):
    bad = []
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        f = Path(directory) / name
        if not f.exists() or sha256(f) != digest:
            bad.append(name)
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    DIR.mkdir(parents=True, exist_ok=True)
    sums = DIR / "SHA256SUMS"
    if not a.verify:
        for snap, (name, url, size) in PDFS.items():
            dest = DIR / name
            if dest.exists() and dest.stat().st_size == size:
                print("have", name)
                continue
            print("fetching", snap, "->", name)
            download(url, dest)
            got = dest.stat().st_size
            if got != size:
                print(f"WARNING size mismatch for {name}: expected {size}, got {got}. If the mirror re-uploaded the file, update PDFS.")
        write_sums([DIR / n for n, _, _ in PDFS.values()], sums)
        print("wrote", sums)
    bad = verify_sums(sums, DIR)
    print("verify:", "OK" if not bad else f"MISMATCH {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
```

`tools/show_page.py`:
```python
"""Print the text (and optionally the extracted tables) of one PDF page, 1-based.
Run: python tools/show_page.py data/pdfs/Flash_Report_April_2026.pdf 3
     python tools/show_page.py data/pdfs/Flash_Report_April_2026.pdf 56 --tables
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber

path, page_no = sys.argv[1], int(sys.argv[2])
with pdfplumber.open(path) as pdf:
    page = pdf.pages[page_no - 1]
    print(page.extract_text() or "<no text layer>")
    if "--tables" in sys.argv:
        settings = {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 3, "join_tolerance": 3, "intersection_tolerance": 3}
        for t_i, table in enumerate(page.extract_tables(settings)):
            print(f"--- table {t_i}: {len(table)} rows")
            for row in table[:6]:
                print([(c or "").replace("\n", "\\n")[:40] for c in row])
```

- [x] **Step 4: Fetch, verify, run the tests**

Run: `python tools/fetch_pdfs.py`
Expected: five `fetching ...` lines (about 33 MB total), `wrote data\pdfs\SHA256SUMS`, `verify: OK`. If a size WARNING appears, open the PDF and confirm it is the right month, then update the size in `PDFS`.

Run: `pytest tests/tools/test_fetch.py -q`
Expected: 3 passed.

- [x] **Step 5: Record the printed aggregates from page 3 of each PDF**

For each PDF run `python tools/show_page.py data/pdfs/<file> 3` and copy the printed totals. Create `data/aggregates.json` (April values are known from the analysis; verify them on the page too):
```json
{
  "2025-12": {"rows_printed": null, "cost_original_cr": null, "cost_revised_cr": null, "expenditure_cum_cr": null, "commissioned": null},
  "2026-04": {"rows_printed": 1981, "cost_original_cr": 3712662, "cost_revised_cr": 4278402, "expenditure_cum_cr": 2036107, "commissioned": null},
  "2026-05": {"rows_printed": null, "cost_original_cr": null, "cost_revised_cr": null, "expenditure_cum_cr": null, "commissioned": null},
  "2026-06": {"rows_printed": null, "cost_original_cr": null, "cost_revised_cr": null, "expenditure_cum_cr": null, "commissioned": null},
  "2026-07": {"rows_printed": null, "cost_original_cr": null, "cost_revised_cr": null, "expenditure_cum_cr": null, "commissioned": null}
}
```
Replace every `null` with the number printed on that report's page 3 (`rows_printed` = the ongoing-projects count, e.g. 1981; costs in crore without commas). If the report prints a "projects commissioned during the month" count (the PIB release for April says 9), put it in `commissioned`; otherwise leave `null`. If page 3 is not the summary page for some month, find it with `show_page` on pages 2–5.

- [x] **Step 6: Do the Day-1 human checks and write them down**

Create `docs/DAY1-CHECKS.md` and answer each line by looking at the PDFs (use `show_page` with `--tables` on the first Table 6 page and on any page containing 705526):
```markdown
# Day-1 checks (facts from the PDFs, dated)

- (a) Does Table 6 print section-header rows naming ministry/sector between project rows? Answer: <yes/no; example text>
- (b) Does the report print a list of projects commissioned during the month, or only a count? Answer: <list on page N / count only / neither>
- (c) Table 6 page range per PDF: 2025-12: <a-b>; 2026-04: 55-162; 2026-05: <a-b>; 2026-06: <a-b>; 2026-07: <a-b>
- (d) Project 705526: cumulative expenditure in Dec 2025 = <x> (page N), Apr 2026 = <y> (page M). Footnote or re-scoping note? <quote or "none found">
- Checked by <name> on <date>.
```
Find the page ranges by running `python tools/show_page.py <pdf> <n> --tables` on a few pages around the expected range and noting the first and last pages whose table has 8 columns and a numeric first cell.

- [x] **Step 7: Run the gate and commit (the PDFs are committed on purpose)**

Run: `python tools/validate.py`
Expected: `RESULT: PASS`.

```powershell
git switch -c task/03-fetch-pdfs
git add -A
git commit -m "task 03: fetch and pin the five Flash Report PDFs, aggregates, day-1 checks"
git push -u origin task/03-fetch-pdfs
gh pr create --title "Task 03: PDFs, checksums, aggregates" --body "validate.py: PASS; pytest: passed; fetch: verify OK"
```

---

### Task 4: Parser core, proven on the April 2026 report

**Files:**
- Create: `parser/extract.py`, `parser/normalize.py`, `parser/adapters.py`, `parser/run.py`
- Test: `tests/parser/test_normalize.py`, `tests/parser/test_extract.py`, `tests/parser/test_april_real.py`

**Interfaces:**
- Consumes: `tools.fetch_pdfs.PDFS`, `data/pdfs/*.pdf`, `data/aggregates.json`.
- Produces: `parser.extract.RawRow(page: int, cells: list[str], section: str | None, spans_page: bool)`; `parser.extract.extract_rows(pdf_path, pages: tuple[int, int] | None) -> list[RawRow]`; `parser.normalize.normalize(raw: RawRow, snapshot: str, source_file: str, sha: str) -> dict` (one canonical row, keys = the 21 panel columns, NULL = `None`); `parser.adapters.ADAPTERS: dict[str, Adapter]`; CLI `python -m parser.run --snapshot 2026-04` writing `data/out/parts/2026-04.csv` and printing row count and column sums.

- [x] **Step 1: Write the failing normalizer tests**

Create `tests/parser/test_normalize.py`:
```python
from parser.extract import RawRow
from parser.normalize import normalize, parse_dates, parse_numbers, split_name


def test_split_name_all_parentheticals():
    r = split_name("Sikkim Road Project (Border Roads Organisation) (612793) (N04000110) (PMG12345)")
    assert r["project_name"] == "Sikkim Road Project"
    assert r["agency_raw"] == "Border Roads Organisation"
    assert r["project_code"] == "612793"
    assert r["legacy_ocms_code"] == "N04000110"
    assert r["pmgid"] == "PMG12345"
    assert r["flags"] == []


def test_split_name_missing_ids_flags():
    r = split_name("Some Project\n(Agency Name Ltd)\n(612794)")
    assert r["project_code"] == "612794" and r["legacy_ocms_code"] is None and r["pmgid"] is None
    assert set(r["flags"]) == {"NO_LEGACY_CODE", "NO_PMGID"}
    r2 = split_name("Nameless Codes (Agency)")
    assert r2["project_code"] is None and "NO_PROJECT_CODE" in r2["flags"]


def test_parse_dates():
    assert parse_dates("11/2023 (01/2024)") == ("2023-11", "2024-01", [])
    assert parse_dates("06/2026\n(06/2027)") == ("2026-06", "2027-06", [])
    assert parse_dates("06/2026") == ("2026-06", None, [])
    assert parse_dates("-") == (None, None, ["DATE_PARSE_FAIL"])


def test_parse_numbers():
    assert parse_numbers("323.26\n350.00") == [323.26, 350.0]
    assert parse_numbers("1,856.36 / 3,800.00") == [1856.36, 3800.0]
    assert parse_numbers("") == []


def test_normalize_sample_row():
    raw = RawRow(page=57, section="Road Transport and Highways", spans_page=False, cells=[
        "12", "Sikkim Road Project (Border Roads Organisation) (612793) (N04000110) (PMG12345)", "Sikkim",
        "11/2023 (01/2024)", "06/2026 (06/2027)", "323.26\n350.00", "80.84", "34.25"])
    row = normalize(raw, "2026-04", "Flash_Report_April_2026.pdf", "a" * 64)
    assert row["snapshot"] == "2026-04" and row["page"] == 57 and row["sl_no"] == 12
    assert row["project_code"] == "612793" and row["state"] == "Sikkim" and row["table_section"] == "Road Transport and Highways"
    assert row["approval_month"] == "2023-11" and row["start_month"] == "2024-01"
    assert row["doc_original"] == "2026-06" and row["doc_revised"] == "2027-06"
    assert row["cost_original_cr"] == 323.26 and row["cost_revised_cr"] == 350.0
    assert row["expenditure_cum_cr"] == 80.84 and row["physical_progress_pct"] == 34.25
    assert row["parse_flags"] == ""
    assert len(row) == 21


def test_normalize_multiline_state_and_missing_numbers():
    raw = RawRow(page=60, section=None, spans_page=True, cells=[
        "13", "Island Jetty (Port Authority) (100012)", "Andaman and\nNicobar Islands", "08/2023", "01/2027", "250.00", "-", "27"])
    row = normalize(raw, "2026-04", "f.pdf", "b" * 64)
    assert row["state"] == "Andaman and Nicobar Islands"
    assert row["expenditure_cum_cr"] is None
    flags = set(row["parse_flags"].split(";"))
    assert {"MULTILINE_STATE", "NUM_PARSE_FAIL", "ROW_SPANS_PAGE", "NO_LEGACY_CODE", "NO_PMGID"} <= flags
```

Create `tests/parser/test_extract.py`:
```python
from parser.extract import merge_tables


def test_merge_tables_handles_header_section_continuation_and_page_span():
    page1 = [
        ["Sl.No", "Project Name", "State", "Date of Approval", "DoC", "Cost", "Expenditure", "Progress"],
        ["Railways", "", "", "", "", "", "", ""],
        ["1", "Alpha Line (Railways) (100001)", "Bihar", "01/2020", "12/2026", "500\n520", "100", "20"],
        ["", "(N04000001) (PMG1)", "", "", "", "", "", ""],
    ]
    page2 = [
        ["", "continued name part", "", "", "", "", "", ""],
        ["2", "Beta Road (NHAI) (100002)", "Gujarat", "02/2021", "06/2027", "900\n950", "500", "60"],
    ]
    rows = merge_tables([(55, [page1]), (56, [page2])])
    assert len(rows) == 2
    assert rows[0].section == "Railways" and rows[0].page == 55
    assert rows[0].cells[1] == "Alpha Line (Railways) (100001)\n(N04000001) (PMG1)\ncontinued name part"
    assert rows[0].spans_page is True
    assert rows[1].cells[0] == "2" and rows[1].spans_page is False
```

- [x] **Step 2: Run them to verify they fail**

Run: `pytest tests/parser -q`
Expected: FAIL with import errors.

- [x] **Step 3: Write `parser/extract.py`**

```python
"""Turn Table 6 pages into RawRow records. Uses pdfplumber's ruling-line strategy; merges wrapped/continuation rows."""
import re
from dataclasses import dataclass, field

import pdfplumber

TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 3,
                  "join_tolerance": 3, "intersection_tolerance": 3}
HEADER_FIRST = re.compile(r"^\s*Sl\.?\s*No", re.I)
SERIAL = re.compile(r"^\s*\d+\s*$")
NCOLS = 8


@dataclass
class RawRow:
    page: int
    cells: list = field(default_factory=list)
    section: str = None
    spans_page: bool = False


def _clean(c):
    return (c or "").replace("\r", "").strip()


def merge_tables(pages_tables):
    """pages_tables: iterable of (page_no, [table, ...]) where table = list of rows (lists of cell strings)."""
    rows, current, section = [], None, None
    for page_no, tables in pages_tables:
        for table in tables:
            for raw in table:
                cells = [_clean(c) for c in raw]
                if len(cells) < NCOLS:
                    cells = cells + [""] * (NCOLS - len(cells))
                cells = cells[:NCOLS]
                nonempty = [c for c in cells if c]
                if not nonempty or HEADER_FIRST.match(cells[0]):
                    continue
                if SERIAL.match(cells[0]):
                    current = RawRow(page=page_no, cells=cells, section=section)
                    rows.append(current)
                    continue
                if cells[0] and len(nonempty) == 1:
                    section = nonempty[0].replace("\n", " ")
                    continue
                if current is not None and not cells[0]:
                    for i, c in enumerate(cells):
                        if c:
                            current.cells[i] = (current.cells[i] + "\n" + c).strip("\n")
                    if page_no != current.page:
                        current.spans_page = True
    return rows


def _has_project_table(page):
    tables = page.extract_tables(TABLE_SETTINGS)
    for t in tables:
        for r in t:
            if r and len(r) >= NCOLS and SERIAL.match(_clean(r[0])):
                return True
    return False


def find_table_pages(pdf):
    """Auto-detect (start, end) 1-based page numbers of the ongoing-projects table. Adapters may override."""
    start = end = None
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        if start is None and "Ongoing Projects" in text and _has_project_table(page):
            start = i
        if start is not None and _has_project_table(page):
            end = i
    if start is None:
        raise RuntimeError("could not find the ongoing-projects table; pass explicit pages in the adapter")
    return start, end


def extract_rows(pdf_path, pages=None):
    with pdfplumber.open(pdf_path) as pdf:
        if pages is None:
            pages = find_table_pages(pdf)
        start, end = pages
        pages_tables = []
        for n in range(start, end + 1):
            pages_tables.append((n, pdf.pages[n - 1].extract_tables(TABLE_SETTINGS)))
        return merge_tables(pages_tables)
```

- [x] **Step 4: Write `parser/normalize.py`**

```python
"""RawRow -> canonical panel row (dict with the 21 columns). NULL = None. Never derives anything."""
import re

COLUMNS = ["snapshot", "source_file", "source_sha256", "page", "sl_no", "project_code", "legacy_ocms_code", "pmgid",
           "project_name", "agency_raw", "table_section", "state", "approval_month", "start_month", "doc_original",
           "doc_revised", "cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct", "parse_flags"]
PAREN = re.compile(r"\(([^()]*)\)")
CODE6 = re.compile(r"^\d{6}$")
LEGACY = re.compile(r"^[A-Z]{1,2}\d{7,9}$")
IDLIKE = re.compile(r"^[A-Za-z0-9/_-]+$")
MONTH = re.compile(r"(\d{1,2})\s*/\s*(\d{4})")
NUMBER = re.compile(r"\d[\d,]*\.?\d*")


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def split_name(cell):
    parens = [_ws(p) for p in PAREN.findall(cell or "")]
    name = _ws(cell.split("(", 1)[0]) if cell else ""
    out = {"project_name": name, "agency_raw": None, "project_code": None, "legacy_ocms_code": None, "pmgid": None, "flags": []}
    for p in parens:
        if not p:
            continue
        if out["project_code"] is None and CODE6.match(p):
            out["project_code"] = p
        elif out["legacy_ocms_code"] is None and LEGACY.match(p):
            out["legacy_ocms_code"] = p
        elif out["agency_raw"] is None and not (IDLIKE.match(p) and out["project_code"] is not None):
            out["agency_raw"] = p
        elif out["pmgid"] is None and IDLIKE.match(p):
            out["pmgid"] = p
        elif out["agency_raw"] is not None:
            out["agency_raw"] = out["agency_raw"] + " " + p
    for key, flag in [("project_code", "NO_PROJECT_CODE"), ("legacy_ocms_code", "NO_LEGACY_CODE"), ("pmgid", "NO_PMGID")]:
        if out[key] is None:
            out["flags"].append(flag)
    return out


def _ym(m):
    mm, yyyy = int(m.group(1)), m.group(2)
    return f"{yyyy}-{mm:02d}" if 1 <= mm <= 12 else None


def parse_dates(cell):
    """Returns (first_token, first_parenthesised_token, flags). Tokens are MM/YYYY -> YYYY-MM."""
    text = cell or ""
    first = paren = None
    for m in MONTH.finditer(text):
        before = text[:m.start()]
        inside = before.count("(") > before.count(")")
        v = _ym(m)
        if inside and paren is None:
            paren = v
        elif not inside and first is None:
            first = v
    flags = [] if first is not None else ["DATE_PARSE_FAIL"]
    return first, paren, flags


def parse_numbers(cell):
    return [float(t.replace(",", "")) for t in NUMBER.findall(cell or "") if t not in (".",)]


def normalize(raw, snapshot, source_file, sha):
    c = raw.cells + [""] * (8 - len(raw.cells))
    flags = []
    ident = split_name(c[1])
    flags += ident.pop("flags")
    state_raw = c[2] or ""
    if "\n" in state_raw.strip():
        flags.append("MULTILINE_STATE")
    approval, start, f1 = parse_dates(c[3])
    doc_o, doc_r, f2 = parse_dates(c[4])
    flags += f1 + f2
    costs = parse_numbers(c[5])
    exp = parse_numbers(c[6])
    prog = parse_numbers(c[7])
    if not costs or not exp or not prog:
        flags.append("NUM_PARSE_FAIL")
    if raw.spans_page:
        flags.append("ROW_SPANS_PAGE")
    row = {
        "snapshot": snapshot, "source_file": source_file, "source_sha256": sha, "page": raw.page, "sl_no": int(c[0]),
        "project_code": ident["project_code"], "legacy_ocms_code": ident["legacy_ocms_code"], "pmgid": ident["pmgid"],
        "project_name": ident["project_name"] or "(unnamed)", "agency_raw": ident["agency_raw"],
        "table_section": _ws(raw.section) if raw.section else None, "state": _ws(state_raw) or None,
        "approval_month": approval, "start_month": start, "doc_original": doc_o, "doc_revised": doc_r,
        "cost_original_cr": costs[0] if costs else None, "cost_revised_cr": costs[1] if len(costs) > 1 else None,
        "expenditure_cum_cr": exp[0] if exp else None, "physical_progress_pct": prog[0] if prog else None,
        "parse_flags": ";".join(dict.fromkeys(flags)),
    }
    assert list(row) == COLUMNS
    return row
```

- [x] **Step 5: Write `parser/adapters.py` and `parser/run.py`**

`parser/adapters.py`:
```python
"""One adapter per snapshot: which file, which pages, what the month is known to omit. Task 5 fills the other four."""
from dataclasses import dataclass

from tools.fetch_pdfs import PDFS


@dataclass(frozen=True)
class Adapter:
    snapshot: str
    file: str
    pages: tuple = None          # (start, end) 1-based; None = auto-detect
    expect_pmgid: bool = True    # False => NO_PMGID is not counted as a miss in the coverage report
    expect_legacy: bool = True


ADAPTERS = {
    "2026-04": Adapter("2026-04", PDFS["2026-04"][0], pages=(55, 162)),
}
```

`parser/run.py`:
```python
"""CLI: python -m parser.run --snapshot 2026-04 [--peek 3]   -> data/out/parts/<snapshot>.csv
        python -m parser.run --merge                          -> data/out/panel.csv + data/out/parse_coverage.md"""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from parser.adapters import ADAPTERS
from parser.extract import extract_rows
from parser.normalize import COLUMNS, normalize
from tools.fetch_pdfs import sha256

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "pdfs"
OUT = ROOT / "data" / "out"
SNAPSHOT_ORDER = ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]


def aggregates():
    p = ROOT / "data" / "aggregates.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def parse_snapshot(snapshot, peek=0):
    ad = ADAPTERS[snapshot]
    pdf = PDF_DIR / ad.file
    sha = sha256(pdf)
    raws = extract_rows(pdf, ad.pages)
    if peek:
        for r in raws[:peek]:
            print(f"page {r.page} section={r.section!r}")
            for c in r.cells:
                print("   ", repr(c))
    rows = [normalize(r, snapshot, ad.file, sha) for r in raws]
    return rows


def write_rows(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})


def report(rows, snapshot):
    agg = aggregates().get(snapshot) or {}
    sums = {k: sum(r[k] for r in rows if r[k] is not None) for k in ["cost_original_cr", "cost_revised_cr", "expenditure_cum_cr"]}
    printed = agg.get("rows_printed")
    pct = round(100 * len(rows) / printed, 2) if printed else None
    flags = Counter(f for r in rows for f in r["parse_flags"].split(";") if f)
    print(f"{snapshot}: {len(rows)} rows parsed" + (f" of {printed} printed ({pct}%)" if printed else " (no printed count recorded)"))
    for k, v in sums.items():
        target = agg.get(k)
        dev = f" vs printed {target} ({100 * (v - target) / target:+.2f}%)" if target else ""
        print(f"  sum {k} = {v:,.2f}{dev}")
    print("  flags:", dict(flags))
    return {"snapshot": snapshot, "rows_parsed": len(rows), "rows_printed": printed, "pct": pct, "sums": sums, "flags": dict(flags)}


def merge():
    parts = [(s, OUT / "parts" / f"{s}.csv") for s in SNAPSHOT_ORDER if (OUT / "parts" / f"{s}.csv").exists()]
    all_rows, lines = [], ["# Parse coverage", ""]
    for s, p in parts:
        with open(p, newline="", encoding="utf-8") as f:
            rows = [{k: (None if v == "" and k != "parse_flags" else v) for k, v in r.items()} for r in csv.DictReader(f)]
        for r in rows:
            for k in ["cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct"]:
                r[k] = float(r[k]) if r[k] is not None else None
            r["page"], r["sl_no"] = int(r["page"]), int(r["sl_no"])
        info = report(rows, s)
        ad = ADAPTERS[s]
        ignored = {f for f, ex in [("NO_PMGID", ad.expect_pmgid), ("NO_LEGACY_CODE", ad.expect_legacy)] if not ex}
        lines.append(f"## {s} — {info['rows_parsed']} parsed" + (f" of {info['rows_printed']} printed ({info['pct']}%)" if info['rows_printed'] else ""))
        for k, v in info["sums"].items():
            lines.append(f"- sum {k}: {v:,.2f}")
        for fl, n in sorted(info["flags"].items()):
            lines.append(f"- flag {fl}: {n}" + (" (expected for this month)" if fl in ignored else ""))
        lines.append("")
        all_rows += rows
    write_rows(all_rows, OUT / "panel.csv")
    (OUT / "parse_coverage.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT / 'panel.csv'} ({len(all_rows)} rows) and parse_coverage.md")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot")
    ap.add_argument("--peek", type=int, default=0)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args(argv)
    if a.snapshot:
        rows = parse_snapshot(a.snapshot, a.peek)
        write_rows(rows, OUT / "parts" / f"{a.snapshot}.csv")
        report(rows, a.snapshot)
    if a.merge:
        merge()
    if not a.snapshot and not a.merge:
        ap.error("give --snapshot <YYYY-MM> and/or --merge")


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 6: Run the unit tests**

Run: `pytest tests/parser -q`
Expected: 7 passed. If `test_split_name_all_parentheticals` fails on `agency_raw`, the classification order in `split_name` is wrong for that input; fix the code, not the test.

- [x] **Step 7: Peek at the real April rows and adjust regexes if the cell layout differs**

Run: `python -m parser.run --snapshot 2026-04 --peek 3`
Expected: three raw rows printed with 8 cells each, then `2026-04: N rows parsed of 1981 printed (P%)` and three sum lines. Read the three raw rows. If the project-name cell puts the codes in a different order, or the cost cell uses a separator the number regex misses, or dates are `MM-YYYY`, change the regex in `parser/normalize.py`, add the real cell text as a new case in `tests/parser/test_normalize.py`, and re-run until `pytest tests/parser -q` passes. Do not change the column contract.

- [x] **Step 8: Add the real-PDF gate test**

Create `tests/parser/test_april_real.py`:
```python
import json
from pathlib import Path

import pytest

from parser.run import parse_snapshot

PDF = Path("data/pdfs/Flash_Report_April_2026.pdf")


@pytest.mark.skipif(not PDF.exists(), reason="April PDF not fetched")
def test_april_parses_at_least_90_percent_and_sums_match():
    rows = parse_snapshot("2026-04")
    agg = json.loads(Path("data/aggregates.json").read_text(encoding="utf-8"))["2026-04"]
    assert len(rows) >= 0.90 * agg["rows_printed"], f"only {len(rows)} rows"
    for k in ["cost_original_cr", "cost_revised_cr", "expenditure_cum_cr"]:
        s = sum(r[k] for r in rows if r[k] is not None)
        assert abs(s - agg[k]) / agg[k] < 0.005, f"{k}: parsed {s:,.0f} vs printed {agg[k]:,.0f}"
    codes = [r["project_code"] for r in rows if r["project_code"]]
    assert len(codes) == len(set(codes)), "duplicate project codes in one snapshot"
```

Run: `pytest tests/parser -q`
Expected: 8 passed (the real test takes ~1–2 minutes). If coverage is between 80% and 90%, look at `--peek` output of pages where the count of serial rows is low (`python tools/show_page.py <pdf> <page> --tables`) and extend `merge_tables` for the pattern you see (typical: a row whose first cell holds `"12\n"` with the name in the same cell — add a `SERIAL_PREFIX = re.compile(r"^\s*(\d+)\s*\n(.*)", re.S)` split before the `SERIAL` check). Coverage below 80% after one hour: stop, hand off with the peek output in the PR.

- [x] **Step 9: Write the part file, run the gate, commit**

Run: `python -m parser.run --snapshot 2026-04` then `python tools/validate.py`
Expected: `data\out\parts\2026-04.csv` written; validator `RESULT: PASS` (panel.csv still SKIP).

```powershell
git switch -c task/04-parser-core
git add -A
git commit -m "task 04: parser core (pdfplumber lines strategy), April 2026 at >=90% coverage"
git push -u origin task/04-parser-core
gh pr create --title "Task 04: parser core on April 2026" --body "<paste validate.py and pytest output, including the April coverage line>"
```

---

### Task 5: The other four adapters, the full panel, the coverage report

**Files:**
- Modify: `parser/adapters.py` (add four entries)
- Create: `data/out/parts/2025-12.csv`, `data/out/parts/2026-05.csv`, `data/out/parts/2026-06.csv`, `data/out/parts/2026-07.csv`, `data/out/panel.csv`, `data/out/parse_coverage.md` (all generated, committed)
- Test: `tests/parser/test_panel_real.py`

**Interfaces:**
- Consumes: Task 4 CLI.
- Produces: `data/out/panel.csv` in `SNAPSHOT_ORDER`, every row valid against `panel.schema.json`; `parse_coverage.md`.

- [x] **Step 1: Write the failing panel gate test**

Create `tests/parser/test_panel_real.py`:
```python
import csv
import json
from collections import Counter
from pathlib import Path

import pytest

PANEL = Path("data/out/panel.csv")


@pytest.mark.skipif(not PANEL.exists(), reason="panel.csv not built")
def test_panel_covers_five_snapshots_at_95_percent():
    agg = json.loads(Path("data/aggregates.json").read_text(encoding="utf-8"))
    with open(PANEL, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts = Counter(r["snapshot"] for r in rows)
    assert set(counts) == {"2025-12", "2026-04", "2026-05", "2026-06", "2026-07"}
    for snap, n in counts.items():
        printed = (agg.get(snap) or {}).get("rows_printed")
        assert printed, f"record rows_printed for {snap} in data/aggregates.json"
        assert n >= 0.95 * printed, f"{snap}: {n} of {printed} ({100 * n / printed:.1f}%)"
    for snap in counts:
        codes = [r["project_code"] for r in rows if r["snapshot"] == snap and r["project_code"]]
        assert len(codes) == len(set(codes)), f"duplicate codes in {snap}"
```

- [x] **Step 2: Add the four adapters**

Edit `parser/adapters.py`, replacing the `ADAPTERS` dict:
```python
ADAPTERS = {
    "2025-12": Adapter("2025-12", PDFS["2025-12"][0], pages=None, expect_pmgid=False, expect_legacy=False),
    "2026-04": Adapter("2026-04", PDFS["2026-04"][0], pages=(55, 162)),
    "2026-05": Adapter("2026-05", PDFS["2026-05"][0], pages=None),
    "2026-06": Adapter("2026-06", PDFS["2026-06"][0], pages=None),
    "2026-07": Adapter("2026-07", PDFS["2026-07"][0], pages=None),
}
```
Then for each of the four, run `python -m parser.run --snapshot <S> --peek 2`. Note the detected page range printed by adding one temporary `print(pages)` in `extract_rows` if needed, and write the confirmed range into the adapter (`pages=(a, b)`) so auto-detection is never relied on again. Remove the temporary print.

- [x] **Step 3: Get each month to ≥ 95%**

For each snapshot, read the coverage line. Where a month falls short, the cause is a layout variant of that month (December 2025 has no PMGID/legacy code — that is expected and flagged, not a miss). Use `python tools/show_page.py <pdf> <page> --tables` on a page whose serial numbers skip, extend `merge_tables`/`normalize` for the variant, add the raw text as a test case in `tests/parser/test_normalize.py` or `test_extract.py`, and re-run `pytest tests/parser -q` before re-parsing. If a month cannot reach 95% within two hours, record the reason in `parse_coverage.md` under that month and continue; the test threshold stays at 95% and the PR notes the exception for the reviewer.

- [x] **Step 4: Merge and verify**

Run: `python -m parser.run --merge` then `pytest -q` then `python tools/validate.py`
Expected: `wrote data\out\panel.csv (N rows)`; pytest all green; validator `ok   data/out/panel.csv: N rows valid`, `RESULT: PASS`.

- [x] **Step 5: Commit the generated data**

```powershell
git switch -c task/05-full-panel
git add -A
git commit -m "task 05: adapters for Dec 2025 and May-Jul 2026; full panel.csv; coverage report"
git push -u origin task/05-full-panel
gh pr create --title "Task 05: five-snapshot panel" --body "<paste validate.py output and the five coverage lines from parse_coverage.md>"
```

---

### Task 6: Findings foundation and F1 Contradiction Ledger

**Files:**
- Create: `findings/panel.py`, `findings/contradictions.py`
- Test: `tests/findings/test_panel.py`, `tests/findings/test_contradictions.py`

**Interfaces:**
- Consumes: `contracts/fixtures/panel.sample.csv`, `data/out/panel.csv`.
- Produces (used by every later findings/model task):
  - `findings.panel.SNAPSHOTS: list[str]`, `months(a: str, b: str) -> int`, `add_months(ym: str, k: int) -> str`
  - `load_panel(path) -> pandas.DataFrame` (numeric columns float with NaN, text columns `None` for NULL, `parse_flags` string)
  - `series(panel) -> dict[str, list[dict]]` project_code → rows ascending by snapshot (NaN already converted to `None`)
  - `snapshots_present(panel) -> list[str]`, `latest(panel) -> str`, `pairs_present(panel) -> list[tuple[str, str, str]]` as `(pair_id, from, to)`
  - `source(row: dict) -> dict` = `{"snapshot", "page"}`, `sector_map(panel) -> dict[str, str]`
  - `findings.contradictions.detect(panel) -> list[dict]`: flag dicts with keys `project_code, type, severity, from_snapshot, to_snapshot, before, after, detail, sources`.

- [x] **Step 1: Write the failing tests**

Create `tests/findings/test_panel.py`:
```python
from findings.panel import add_months, latest, load_panel, months, pairs_present, sector_map, series, snapshots_present

FIX = "contracts/fixtures/panel.sample.csv"


def test_months_and_add_months():
    assert months("2025-12", "2026-04") == 4
    assert months("2026-07", "2026-07") == 0
    assert months("2026-07", "2026-03") == -4
    assert add_months("2025-12", 1) == "2026-01"
    assert add_months("2026-07", 11) == "2027-06"


def test_load_and_series():
    panel = load_panel(FIX)
    assert len(panel) == 52
    assert panel["expenditure_cum_cr"].dtype.kind == "f"
    ser = series(panel)
    assert len(ser) == 12
    assert [r["snapshot"] for r in ser["100007"]] == ["2025-12", "2026-04", "2026-05"]
    assert ser["100012"][0]["snapshot"] == "2026-04"  # the Dec row has no code and is excluded
    assert ser["100001"][0]["doc_revised"] is None and ser["100001"][0]["pmgid"] is None


def test_snapshots_pairs_latest_sector():
    panel = load_panel(FIX)
    assert snapshots_present(panel) == ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
    assert latest(panel) == "2026-07"
    assert pairs_present(panel) == [("P1", "2025-12", "2026-04"), ("P2", "2026-04", "2026-05"), ("P3", "2026-05", "2026-06"), ("P4", "2026-06", "2026-07")]
    assert sector_map(panel)["100001"] == "Road Transport and Highways"
```

Create `tests/findings/test_contradictions.py`:
```python
from findings.contradictions import detect
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def by(flags, code, typ):
    return [f for f in flags if f["project_code"] == code and f["type"] == typ]


def test_every_planted_contradiction_is_found():
    flags = detect(load_panel(FIX))
    f = by(flags, "100002", "EXP_DECREASE")
    assert len(f) == 1 and f[0]["severity"] == "critical" and (f[0]["from_snapshot"], f[0]["to_snapshot"]) == ("2026-04", "2026-05")
    assert f[0]["before"] == 620.0 and f[0]["after"] == 120.0 and f[0]["sources"] == [{"snapshot": "2026-04", "page": 56}, {"snapshot": "2026-05", "page": 57}]
    g = by(flags, "100003", "PROG_DECREASE")
    assert len(g) == 1 and g[0]["severity"] == "high" and g[0]["to_snapshot"] == "2026-06"
    assert {x["to_snapshot"] for x in by(flags, "100004", "EXP_GT_REVISED_COST")} == {"2026-06", "2026-07"}
    assert len(by(flags, "100005", "ZERO_PROG_NONZERO_EXP")) == 5
    assert len(by(flags, "100011", "PROG_GT_100")) == 1 and len(by(flags, "100011", "DOC_BEFORE_APPROVAL")) == 5
    d = by(flags, "100006", "DOC_REVISED_FILED")
    assert len(d) == 1 and d[0]["before"] == "2026-12" and d[0]["after"] == "2027-06" and d[0]["severity"] == "info"
    c = by(flags, "100010", "COST_REVISED_FILED")
    assert len(c) == 1 and c[0]["before"] == 800.0 and c[0]["after"] == 1600.0
    assert not [x for x in flags if x["project_code"] == "100001"]


def test_flags_are_sorted_and_have_required_keys():
    flags = detect(load_panel(FIX))
    keys = {"project_code", "type", "severity", "from_snapshot", "to_snapshot", "before", "after", "detail", "sources"}
    assert all(set(f) == keys for f in flags)
    assert flags == sorted(flags, key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
```

- [x] **Step 2: Run them to verify they fail**

Run: `pytest tests/findings -q`
Expected: FAIL with import errors.

- [x] **Step 3: Write `findings/panel.py`**

```python
"""The single loader and date helper. Every findings module and model imports from here; nobody re-reads the CSV."""
import math
from collections import Counter, defaultdict

import pandas as pd

SNAPSHOTS = ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]
PAIR_IDS = {("2025-12", "2026-04"): "P1", ("2026-04", "2026-05"): "P2", ("2026-05", "2026-06"): "P3", ("2026-06", "2026-07"): "P4"}
NUMERIC = ["cost_original_cr", "cost_revised_cr", "expenditure_cum_cr", "physical_progress_pct"]
INTS = ["page", "sl_no"]
ORDER = {s: i for i, s in enumerate(SNAPSHOTS)}


def months(a, b):
    return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))


def add_months(ym, k):
    t = int(ym[:4]) * 12 + (int(ym[5:7]) - 1) + k
    return f"{t // 12:04d}-{t % 12 + 1:02d}"


def load_panel(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c].where(df[c] != "", None), errors="coerce")
    for c in INTS:
        df[c] = df[c].astype(int)
    for c in df.columns:
        if c not in NUMERIC + INTS + ["parse_flags"]:
            df[c] = df[c].where(df[c] != "", None).astype(object)
    df["_o"] = df["snapshot"].map(ORDER)
    df = df.sort_values(["_o", "sl_no"]).drop(columns="_o").reset_index(drop=True)
    return df


def _clean(rec):
    return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in rec.items()}


def rows(panel):
    return [_clean(r) for r in panel.to_dict("records")]


def series(panel):
    """project_code -> rows ascending by snapshot; only rows with a code; duplicates within a snapshot keep the last."""
    out = defaultdict(dict)
    for r in rows(panel):
        if r["project_code"]:
            out[r["project_code"]][r["snapshot"]] = r
    return {code: [d[s] for s in SNAPSHOTS if s in d] for code, d in sorted(out.items())}


def snapshots_present(panel):
    present = set(panel["snapshot"])
    return [s for s in SNAPSHOTS if s in present]


def latest(panel):
    return snapshots_present(panel)[-1]


def pairs_present(panel):
    s = snapshots_present(panel)
    return [(PAIR_IDS.get((a, b), f"{a}_{b}"), a, b) for a, b in zip(s, s[1:])]


def source(row):
    return {"snapshot": row["snapshot"], "page": int(row["page"])}


def sector_map(panel):
    """table_section if the PDF printed section headers; else a top-10 agency rollup (D15). None -> 'UNKNOWN'."""
    ser = series(panel)
    if any(r["table_section"] for rs in ser.values() for r in rs):
        return {code: next((r["table_section"] for r in reversed(rs) if r["table_section"]), "UNKNOWN") for code, rs in ser.items()}
    last = latest(panel)
    counts = Counter(r["agency_raw"] for rs in ser.values() for r in rs if r["snapshot"] == last and r["agency_raw"])
    top = {a for a, _ in counts.most_common(10)}
    out = {}
    for code, rs in ser.items():
        agency = next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None)
        out[code] = "UNKNOWN" if agency is None else (agency if agency in top else "OTHER")
    return out
```

- [x] **Step 4: Write `findings/contradictions.py`**

```python
"""F1: arithmetic contradictions within and between consecutive reports. Deterministic; no thresholds beyond the spec."""
from findings.panel import series, source


def _flag(code, typ, sev, a, b, before, after, detail, sources):
    return {"project_code": code, "type": typ, "severity": sev, "from_snapshot": a, "to_snapshot": b,
            "before": before, "after": after, "detail": detail, "sources": sources}


def _cr(x):
    return f"₹{x:,.2f} cr"


def detect(panel):
    flags = []
    for code, rs in series(panel).items():
        for r in rs:
            s, exp, cr, prog = r["snapshot"], r["expenditure_cum_cr"], r["cost_revised_cr"], r["physical_progress_pct"]
            src = [source(r)]
            if exp is not None and cr is not None and exp > cr + 0.005:
                flags.append(_flag(code, "EXP_GT_REVISED_COST", "medium", None, s, cr, exp,
                                   f"Cumulative expenditure {_cr(exp)} exceeds the revised cost {_cr(cr)} in {s}.", src))
            if prog is not None and prog == 0 and exp is not None and exp > 0:
                flags.append(_flag(code, "ZERO_PROG_NONZERO_EXP", "low", None, s, prog, exp,
                                   f"Physical progress is 0% while cumulative expenditure is {_cr(exp)} in {s}.", src))
            if prog is not None and prog > 100:
                flags.append(_flag(code, "PROG_GT_100", "medium", None, s, None, prog,
                                   f"Physical progress is reported as {prog:g}% in {s}.", src))
            if r["doc_original"] and r["approval_month"] and r["doc_original"] < r["approval_month"]:
                flags.append(_flag(code, "DOC_BEFORE_APPROVAL", "low", None, s, r["approval_month"], r["doc_original"],
                                   f"Original completion date {r['doc_original']} is before the approval month {r['approval_month']} in {s}.", src))
        for a, b in zip(rs, rs[1:]):
            sa, sb, src = a["snapshot"], b["snapshot"], [source(a), source(b)]
            ea, eb = a["expenditure_cum_cr"], b["expenditure_cum_cr"]
            if ea is not None and eb is not None and eb < ea - 0.01:
                sev = "critical" if (ea - eb) >= 0.10 * ea else "high"
                flags.append(_flag(code, "EXP_DECREASE", sev, sa, sb, ea, eb,
                                   f"Cumulative expenditure falls from {_cr(ea)} in {sa} to {_cr(eb)} in {sb}; a cumulative field cannot decrease.", src))
            pa, pb = a["physical_progress_pct"], b["physical_progress_pct"]
            if pa is not None and pb is not None and pb < pa - 0.01:
                sev = "high" if (pa - pb) >= 5 else "medium"
                flags.append(_flag(code, "PROG_DECREASE", sev, sa, sb, pa, pb,
                                   f"Physical progress falls from {pa:g}% in {sa} to {pb:g}% in {sb}.", src))
            if a["doc_revised"] != b["doc_revised"]:
                flags.append(_flag(code, "DOC_REVISED_FILED", "info", sa, sb, a["doc_revised"], b["doc_revised"],
                                   f"Revised completion date changed from {a['doc_revised'] or 'none'} to {b['doc_revised'] or 'none'} between {sa} and {sb}.", src))
            ca, cb = a["cost_revised_cr"], b["cost_revised_cr"]
            if ca != cb and not (ca is None and cb is None):
                flags.append(_flag(code, "COST_REVISED_FILED", "info", sa, sb, ca, cb,
                                   f"Revised cost changed from {_cr(ca) if ca is not None else 'none'} to {_cr(cb) if cb is not None else 'none'} between {sa} and {sb}.", src))
    flags.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return flags
```

- [x] **Step 5: Run tests, gate, commit**

Run: `pytest tests/findings -q` → Expected: 5 passed. Run: `python tools/validate.py` → `RESULT: PASS`.

```powershell
git switch -c task/06-findings-f1
git add -A
git commit -m "task 06: panel loader and F1 contradiction ledger"
git push -u origin task/06-findings-f1
gh pr create --title "Task 06: findings foundation + F1" --body "<paste outputs>"
```

---

### Task 7: F2 Exit Ledger and F3 Unreachable-DoC early warning

**Files:**
- Create: `findings/exits.py`, `findings/early_warning.py`
- Test: `tests/findings/test_exits.py`, `tests/findings/test_early_warning.py`

**Interfaces:**
- Consumes: Task 6 `panel` helpers.
- Produces: `findings.exits.compute(panel, aggregates: dict | None) -> {"pairs": [...], "rows": [...], "status": {code: (status, first_seen, last_seen)}}`; `findings.early_warning.velocity(rows) -> float | None`, `assess(rows) -> dict | None` (keys `type, severity, velocity, months_needed, months_remaining, ratio, detail`), `compute(panel) -> {"rows": [...], "flags": [...]}`.

- [x] **Step 1: Write the failing tests**

Create `tests/findings/test_exits.py`:
```python
from findings.exits import compute
from findings.panel import load_panel

FIX = "contracts/fixtures/panel.sample.csv"


def test_exits_and_entries_per_pair():
    ex = compute(load_panel(FIX), aggregates={"2026-05": {"commissioned": 9}})
    pairs = {(p["from"], p["to"]): p for p in ex["pairs"]}
    assert pairs[("2026-04", "2026-05")]["exited"] == 1 and pairs[("2026-04", "2026-05")]["commissioned_printed"] == 9
    assert pairs[("2026-05", "2026-06")]["exited"] == 1 and pairs[("2026-05", "2026-06")]["entered"] == 1
    assert pairs[("2026-06", "2026-07")]["exited"] == 0 and pairs[("2026-06", "2026-07")]["commissioned_printed"] is None
    rows = {r["project_code"]: r for r in ex["rows"]}
    assert rows["100008"]["partition"] == "LAST_SEEN_LT_50" and rows["100008"]["last_seen"] == "2026-04"
    assert rows["100007"]["partition"] == "LAST_SEEN_GE_95" and rows["100007"]["last_progress_pct"] == 97.0
    assert rows["100007"]["sources"] == [{"snapshot": "2026-05", "page": 57}]
    assert ex["status"]["100008"] == ("exited", "2025-12", "2026-04")
    assert ex["status"]["100009"] == ("ongoing", "2026-06", "2026-07")
```

Create `tests/findings/test_early_warning.py`:
```python
import pytest

from findings.early_warning import assess, compute, velocity
from findings.panel import load_panel, series

FIX = "contracts/fixtures/panel.sample.csv"


def test_velocity_is_ols_slope_in_points_per_month():
    rows = [{"snapshot": "2025-12", "physical_progress_pct": 20.0}, {"snapshot": "2026-04", "physical_progress_pct": 28.0},
            {"snapshot": "2026-07", "physical_progress_pct": 34.0}]
    assert velocity(rows) == pytest.approx(2.0, abs=0.05)
    assert velocity(rows[:1]) is None


def test_assess_classes():
    ser = series(load_panel(FIX))
    a = assess(ser["100005"])
    assert a["type"] == "DOC_PASSED" and a["months_remaining"] < 0
    b = assess(ser["100006"])
    assert b["type"] == "DOC_UNREACHABLE" and b["severity"] == "critical" and b["ratio"] > 2
    assert assess(ser["100001"]) is None      # reachable at its own pace
    assert assess(ser["100011"]) is None      # already >= 100


def test_compute_rows_and_flags():
    out = compute(load_panel(FIX))
    codes = {r["project_code"] for r in out["rows"]}
    assert "100006" in codes and "100001" not in codes
    ratios = [r["ratio"] for r in out["rows"] if r["ratio"] is not None]
    assert ratios == sorted(ratios, reverse=True)
    f = [x for x in out["flags"] if x["project_code"] == "100006"][0]
    assert f["type"] == "DOC_UNREACHABLE" and f["to_snapshot"] == "2026-07" and f["from_snapshot"] == "2025-12"
    assert "needs" in f["detail"] and "leaves" in f["detail"]
```

- [x] **Step 2: Run them to verify they fail**

Run: `pytest tests/findings -q` → Expected: import errors for the two new modules.

- [x] **Step 3: Write `findings/exits.py`**

```python
"""F2: projects that leave the monitored panel between consecutive reports, with their last observed state."""
from findings.panel import pairs_present, series, snapshots_present, source


def _partition(prog):
    if prog is None:
        return "UNKNOWN"
    if prog >= 95:
        return "LAST_SEEN_GE_95"
    if prog >= 50:
        return "LAST_SEEN_50_95"
    return "LAST_SEEN_LT_50"


def compute(panel, aggregates=None):
    ser = series(panel)
    snaps = snapshots_present(panel)
    present = {s: {} for s in snaps}
    for code, rs in ser.items():
        for r in rs:
            present[r["snapshot"]][code] = r
    pairs, rows, seen = [], [], set()
    for pid, a, b in pairs_present(panel):
        exited = sorted(set(present[a]) - set(present[b]))
        entered = sorted(set(present[b]) - set(present[a]))
        agg_b = (aggregates or {}).get(b) or {}
        pairs.append({"from": a, "to": b, "exited": len(exited), "entered": len(entered),
                      "exited_cost_revised_cr": round(sum(present[a][c]["cost_revised_cr"] or 0.0 for c in exited), 2),
                      "commissioned_printed": agg_b.get("commissioned")})
        for code in exited:
            last = present[a][code]
            if (code, a) in seen:
                continue
            seen.add((code, a))
            rows.append({"project_code": code, "project_name": last["project_name"], "last_seen": a,
                         "last_progress_pct": last["physical_progress_pct"], "last_expenditure_cr": last["expenditure_cum_cr"],
                         "last_cost_revised_cr": last["cost_revised_cr"], "partition": _partition(last["physical_progress_pct"]),
                         "sources": [source(last)]})
    status = {}
    for code, rs in ser.items():
        first, last = rs[0]["snapshot"], rs[-1]["snapshot"]
        status[code] = ("ongoing" if last == snaps[-1] else "exited", first, last)
    return {"pairs": pairs, "rows": rows, "status": status}
```

- [x] **Step 4: Write `findings/early_warning.py`**

```python
"""F3: can the project reach 100% by its own stated date at its own reported pace? No model, no training set."""
import numpy as np

from findings.panel import months, series, source


def velocity(rows):
    pts = [(months(rows[0]["snapshot"], r["snapshot"]), r["physical_progress_pct"]) for r in rows if r["physical_progress_pct"] is not None]
    if len(pts) < 2 or len({x for x, _ in pts}) < 2:
        return None
    x, y = zip(*pts)
    return float(np.polyfit(x, y, 1)[0])


def doc_current(row):
    return row["doc_revised"] or row["doc_original"]


def assess(rows):
    """rows: a project's rows ascending. Returns a dict for DOC_PASSED / DOC_UNREACHABLE, or None when not flagged."""
    last = rows[-1]
    prog = last["physical_progress_pct"]
    doc = doc_current(last)
    if prog is None or prog >= 100 or doc is None:
        return None
    rem = months(last["snapshot"], doc)
    v = velocity(rows)
    if rem <= 0:
        return {"type": "DOC_PASSED", "severity": "high", "velocity": v, "months_needed": None, "months_remaining": rem, "ratio": None,
                "detail": f"The stated completion date {doc} has passed and reported progress is {prog:g}%."}
    if v is None:
        return None
    if v <= 0:
        n = months(rows[0]["snapshot"], last["snapshot"])
        return {"type": "DOC_UNREACHABLE", "severity": "critical", "velocity": v, "months_needed": None, "months_remaining": rem, "ratio": None,
                "detail": f"No reported progress over {n} months; at this pace the stated date {doc} cannot be met."}
    need = (100 - prog) / v
    ratio = need / rem
    if ratio <= 1:
        return None
    sev = "critical" if ratio >= 2.0 else "high" if ratio >= 1.25 else "medium"
    return {"type": "DOC_UNREACHABLE", "severity": sev, "velocity": v, "months_needed": need, "months_remaining": rem, "ratio": ratio,
            "detail": f"At its own reported pace ({v:.2f} pt/month), this project needs {need:.0f} months; its own stated date {doc} leaves {rem}."}


def compute(panel):
    rows_out, flags = [], []
    for code, rs in series(panel).items():
        a = assess(rs)
        if a is None:
            continue
        srcs = [source(r) for r in rs]
        rows_out.append({"project_code": code, "project_name": rs[-1]["project_name"], "velocity_pct_per_month": a["velocity"],
                         "months_needed": a["months_needed"], "months_remaining": a["months_remaining"], "ratio": a["ratio"],
                         "severity": a["severity"], "sources": srcs})
        flags.append({"project_code": code, "type": a["type"], "severity": a["severity"], "from_snapshot": rs[0]["snapshot"],
                      "to_snapshot": rs[-1]["snapshot"], "before": doc_current(rs[-1]), "after": rs[-1]["physical_progress_pct"],
                      "detail": a["detail"], "sources": srcs})
    rows_out.sort(key=lambda r: (-(r["ratio"] if r["ratio"] is not None else 1e9), r["project_code"]))
    flags.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return {"rows": rows_out, "flags": flags}
```

- [x] **Step 5: Run tests, gate, commit**

Run: `pytest tests/findings -q` → Expected: all passed. Run: `python tools/validate.py` → `RESULT: PASS`.

```powershell
git switch -c task/07-exits-warning
git add -A
git commit -m "task 07: F2 exit ledger and F3 unreachable-DoC early warning"
git push -u origin task/07-exits-warning
gh pr create --title "Task 07: exits and early warning" --body "<paste outputs>"
```

---

### Task 8: F4 risk score, F5 field audit, F6 disclosure lag

**Files:**
- Create: `findings/risk.py`, `findings/field_audit.py`, `findings/disclosure_lag.py`
- Test: `tests/findings/test_risk_fields_lag.py`

**Interfaces:**
- Consumes: Tasks 6–7.
- Produces: `findings.risk.score(flags: list[dict]) -> {"score": float, "band": str, "reasons": list[str]}`; `findings.field_audit.compute(panel) -> dict` (matches `findings.field_audit` schema); `findings.disclosure_lag.compute(panel) -> dict` (matches `findings.disclosure_lag` schema).

- [x] **Step 1: Write the failing tests**

Create `tests/findings/test_risk_fields_lag.py`:
```python
from findings.contradictions import detect
from findings.disclosure_lag import compute as lag
from findings.early_warning import compute as ew
from findings.field_audit import compute as fields
from findings.panel import load_panel
from findings.risk import score

FIX = "contracts/fixtures/panel.sample.csv"


def flags_for(code):
    panel = load_panel(FIX)
    allf = detect(panel) + ew(panel)["flags"]
    return [f for f in allf if f["project_code"] == code]


def test_risk_weights_bands_and_reasons():
    r5 = score(flags_for("100005"))          # 5 x ZERO_PROG (5 each) + DOC_PASSED (25) = 50
    assert r5["score"] == 50 and r5["band"] == "amber" and len(r5["reasons"]) == 6
    r2 = score(flags_for("100002"))          # EXP_DECREASE 20 + DOC_UNREACHABLE critical 40 = 60
    assert r2["score"] == 60 and r2["band"] == "red"
    assert score([]) == {"score": 0, "band": "green", "reasons": []}
    assert score(flags_for("100005") * 3)["score"] == 100


def test_field_audit_shapes():
    fa = fields(load_panel(FIX))
    assert fa["snapshot"] == "2026-07"
    assert sum(d["count"] for d in fa["terminal_digit"]) == 10 and [d["digit"] for d in fa["terminal_digit"]] == list(range(10))
    assert fa["whole_number_share"] == 1.0 and 0 <= fa["multiple_of_5_share"] <= 1
    assert fa["staleness_by_agency"] == []   # no agency has 5 projects in the fixture


def test_disclosure_lag_backcasts_100006():
    out = lag(load_panel(FIX))
    assert out["status"] == "computed"
    rows = {r["project_code"]: r for r in out["rows"]}
    assert rows["100006"]["filed_at"] == "2026-05" and rows["100006"]["first_unreachable"] == "2026-04" and rows["100006"]["lag_months"] == 1
    assert out["median_lag_months"] == 1
```

- [x] **Step 2: Run to verify failure**

Run: `pytest tests/findings/test_risk_fields_lag.py -q` → Expected: import errors.

- [x] **Step 3: Write `findings/risk.py`**

```python
"""F4: transparent rule-based risk score. v1 weights chosen for legibility, not fitted (say so on the slide). Never blended with M1."""
WEIGHTS = {("DOC_UNREACHABLE", "critical"): 40, ("DOC_UNREACHABLE", "high"): 25, ("DOC_UNREACHABLE", "medium"): 10,
           "DOC_PASSED": 25, "EXP_DECREASE": 20, "PROG_DECREASE": 15, "EXP_GT_REVISED_COST": 10,
           "ZERO_PROG_NONZERO_EXP": 5, "DOC_REVISED_FILED": 10, "COST_REVISED_FILED": 5}


def score(flags):
    total, reasons = 0, []
    for f in flags:
        w = WEIGHTS.get((f["type"], f["severity"]), WEIGHTS.get(f["type"], 0))
        if w:
            total += w
            reasons.append(f["detail"])
    s = min(100, total)
    band = "red" if s >= 60 else "amber" if s >= 30 else "green"
    return {"score": s, "band": band, "reasons": reasons}
```

- [x] **Step 4: Write `findings/field_audit.py`**

```python
"""F5: which reported fields look measured and which look guessed. Terminal-digit clustering + per-agency staleness."""
import math
from collections import Counter, defaultdict

from findings.panel import latest, series


def compute(panel):
    last = latest(panel)
    ser = series(panel)
    vals = [r["physical_progress_pct"] for rs in ser.values() for r in rs if r["snapshot"] == last and r["physical_progress_pct"] is not None]
    n = len(vals)
    digits = Counter(int(math.floor(v)) % 10 for v in vals)
    whole = [v for v in vals if float(v).is_integer()]
    by_agency = defaultdict(list)
    for code, rs in ser.items():
        if len(rs) < 2:
            continue
        agency = next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None)
        if agency is None:
            continue
        exps = [r["expenditure_cum_cr"] for r in rs]
        unchanged = all(a is not None and b is not None and a == b for a, b in zip(exps, exps[1:]))
        by_agency[agency].append(unchanged)
    stale = [{"agency_raw": a, "projects": len(v), "share_unchanged": round(sum(v) / len(v), 4)}
             for a, v in sorted(by_agency.items()) if len(v) >= 5]
    stale.sort(key=lambda d: (-d["share_unchanged"], d["agency_raw"]))
    return {"snapshot": last,
            "terminal_digit": [{"digit": d, "count": digits.get(d, 0), "share": round(digits.get(d, 0) / n, 4) if n else 0.0} for d in range(10)],
            "whole_number_share": round(len(whole) / n, 4) if n else 0.0,
            "multiple_of_5_share": round(sum(1 for v in whole if int(v) % 5 == 0) / n, 4) if n else 0.0,
            "multiple_of_10_share": round(sum(1 for v in whole if int(v) % 10 == 0) / n, 4) if n else 0.0,
            "staleness_by_agency": stale}
```

- [x] **Step 5: Write `findings/disclosure_lag.py`**

```python
"""F6: for each revised-DoC filing, the earliest earlier report at which F3 already said the then-stated date was unreachable."""
import statistics

from findings.early_warning import assess
from findings.panel import months, series


def compute(panel):
    rows, any_backcastable = [], False
    for code, rs in series(panel).items():
        for k in range(1, len(rs)):
            if rs[k]["doc_revised"] == rs[k - 1]["doc_revised"]:
                continue
            filed_at = rs[k]["snapshot"]
            first = None
            for j in range(1, k):                      # prefixes rs[:j+1] with >= 2 snapshots, strictly before the filing
                any_backcastable = True
                a = assess(rs[:j + 1])
                if a is not None and a["type"] == "DOC_UNREACHABLE":
                    first = rs[j]["snapshot"]
                    break
            rows.append({"project_code": code, "filed_at": filed_at, "first_unreachable": first,
                         "lag_months": months(first, filed_at) if first else None})
    lags = [r["lag_months"] for r in rows if r["lag_months"] is not None]
    return {"status": "computed" if any_backcastable else "not_computed",
            "median_lag_months": float(statistics.median(lags)) if lags else None, "rows": rows}
```

- [x] **Step 6: Run tests, gate, commit**

Run: `pytest -q` → all green. `python tools/validate.py` → `RESULT: PASS`.

```powershell
git switch -c task/08-risk-fields-lag
git add -A
git commit -m "task 08: F4 risk score, F5 field audit, F6 disclosure lag"
git push -u origin task/08-risk-fields-lag
gh pr create --title "Task 08: risk, field audit, disclosure lag" --body "<paste outputs>"
```

---

### Task 9: Assemble `projects.json` and `findings.json`, assistant, review pack, golden fixtures, page images

**Files:**
- Create: `findings/assistant.py`, `findings/run.py`, `tools/render_pages.py`, `contracts/fixtures/projects.sample.json`, `contracts/fixtures/findings.sample.json` (generated goldens — this task may write under `contracts/fixtures/`), `web/public/data/projects.json`, `web/public/data/findings.json`, `deck/numbers.json` (generated, committed), `web/public/pages/**.png` (generated, committed)
- Test: `tests/findings/test_run_fixture.py`

**Interfaces:**
- Consumes: Tasks 6–8; `data/aggregates.json`.
- Produces: CLI `python -m findings.run --panel <csv> --out <dir> [--no-models] [--deck deck/numbers.json]`; module functions `findings.run.build(panel, aggregates, with_models: bool) -> (projects: list, findings: dict, models: dict | None, model_card: dict | None)` and `write_json(path, obj)`; the hook `findings.run.run_models(panel, flags, sectors) -> (models_json, ml_by_code, extra_flags, model_card)`

- [x] **Step 1: Write the failing test**

Create `tests/findings/test_run_fixture.py`:
```python
import json
import subprocess
import sys
from pathlib import Path


def run(out):
    env = {"AGRIM_GENERATED_AT": "test", "OMP_NUM_THREADS": "1"}
    import os
    p = subprocess.run([sys.executable, "-m", "findings.run", "--panel", "contracts/fixtures/panel.sample.csv", "--out", str(out),
                        "--no-models", "--deck", str(out / "numbers.json")], capture_output=True, text=True, env={**os.environ, **env})
    assert p.returncode == 0, p.stdout + p.stderr
    return json.loads((out / "projects.json").read_text(encoding="utf-8")), json.loads((out / "findings.json").read_text(encoding="utf-8"))


def test_fixture_run_shapes(tmp_path):
    projects, findings = run(tmp_path)
    by = {p["project_code"]: p for p in projects}
    assert len(projects) == 12 and by["100008"]["status"] == "exited" and by["100009"]["first_seen"] == "2026-06"
    assert all(p["ml"] is None for p in projects)
    assert by["100002"]["risk"]["band"] == "red" and any(f["type"] == "EXP_DECREASE" for f in by["100002"]["flags"])
    assert "project_code" not in by["100002"]["flags"][0]
    assert findings["meta"]["generated_at"] == "test" and findings["meta"]["snapshots"][-1] == "2026-07"
    h = findings["meta"]["headline"]
    assert h["projects_latest"] == 10 and h["exits_total"] == 2 and h["contradictions_total"] >= 10 and h["watchlist_size"] == 0
    assert {r["type"] for r in findings["contradictions"]["rows"]} >= {"EXP_DECREASE", "PROG_DECREASE"}
    assert len(findings["assistant"]) == 8 and all(a["answer"] for a in findings["assistant"])
    assert any(r["project_code"] == "100002" for r in findings["review_pack"])
    assert {g["key"] for g in findings["by_sector"]} >= {"Power", "Railways"}
    nums = json.loads((tmp_path / "numbers.json").read_text(encoding="utf-8"))
    assert nums["projects_latest"] == 10 and nums["opener_code"] == "100002"


def test_two_runs_are_byte_identical(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    run(a); run(b)
    for name in ["projects.json", "findings.json"]:
        assert (a / name).read_bytes() == (b / name).read_bytes()
```

- [x] **Step 2: Run to verify failure**

Run: `pytest tests/findings/test_run_fixture.py -q` → Expected: FAIL (`No module named findings.run`).

- [x] **Step 3: Write `findings/assistant.py`**

```python
"""Eight fixed questions answered from the assembled findings with per-number provenance. No model, no network."""


def _top_risk(projects):
    ranked = sorted(projects, key=lambda p: (-p["risk"]["score"], p["project_code"]))
    return ranked[0] if ranked else None


def _fmt(x):
    return f"₹{x:,.2f} cr" if isinstance(x, (int, float)) else str(x)


def build(findings, projects, models=None):
    snaps = findings["meta"]["snapshots"]
    t0, t1 = (snaps[-2], snaps[-1]) if len(snaps) >= 2 else (snaps[0], snaps[0])
    by = {p["project_code"]: p for p in projects}
    out = []
    exp_rows = [r for r in findings["contradictions"]["rows"] if r["type"] == "EXP_DECREASE" and r["from_snapshot"] == t0 and r["to_snapshot"] == t1]
    out.append({"id": 1, "question": f"Which projects report cumulative expenditure falling between {t0} and {t1}?",
                "answer": (f"{len(exp_rows)} project(s). " + "; ".join(f"{r['project_code']} {r['project_name']}: {_fmt(r['before'])} → {_fmt(r['after'])} (page {r['sources'][-1]['page']})" for r in exp_rows[:5])) if exp_rows else f"None between {t0} and {t1}.",
                "sources": [s for r in exp_rows[:5] for s in r["sources"]]})
    ew = findings["early_warning"]["rows"]
    out.append({"id": 2, "question": "Which projects cannot reach their stated completion date at their own reported pace?",
                "answer": f"{len(ew)} project(s) are flagged. Worst five: " + "; ".join(f"{r['project_code']} (ratio {r['ratio']:.1f})" if r['ratio'] else f"{r['project_code']} (no progress)" for r in ew[:5]) if ew else "None flagged.",
                "sources": [s for r in ew[:5] for s in r["sources"]]})
    pair = next((p for p in findings["exits"]["pairs"] if p["from"] == t0 and p["to"] == t1), None)
    ex_rows = [r for r in findings["exits"]["rows"] if r["last_seen"] == t0]
    parts = {}
    for r in ex_rows:
        parts[r["partition"]] = parts.get(r["partition"], 0) + 1
    out.append({"id": 3, "question": f"What left the monitored panel between {t0} and {t1}, and in what state?",
                "answer": (f"{pair['exited']} project(s) left and {pair['entered']} entered. Last observed progress of those that left: " + ", ".join(f"{k}: {v}" for k, v in sorted(parts.items())) + (f". The report prints {pair['commissioned_printed']} commissioned in {t1}." if pair.get("commissioned_printed") is not None else ". The report's commissioned count was not captured.")) if pair else "No pair available.",
                "sources": [s for r in ex_rows[:5] for s in r["sources"]]})
    st = sorted(findings["by_state"], key=lambda g: (-g["flagged"], g["key"]))
    out.append({"id": 4, "question": "Which state has the most flagged projects?",
                "answer": f"{st[0]['key']}: {st[0]['flagged']} of {st[0]['projects']} projects carry at least one flag." if st else "No state data.", "sources": []})
    fa = findings["field_audit"]
    out.append({"id": 5, "question": "How reliable is the Physical Progress field as filled?",
                "answer": f"In {fa['snapshot']}, {fa['whole_number_share']:.0%} of reported progress values are whole numbers, {fa['multiple_of_5_share']:.0%} are multiples of 5 and {fa['multiple_of_10_share']:.0%} multiples of 10. A continuously measured field would show about 1%, 20% and 10% of whole numbers respectively.", "sources": []})
    cov = findings["meta"]["coverage"]
    out.append({"id": 6, "question": "What share of the source reports did AGRIM parse?",
                "answer": "; ".join(f"{c['snapshot']}: {c['rows_parsed']} rows" + (f" of {c['rows_printed']} ({c['pct']}%)" if c["rows_printed"] else "") for c in cov), "sources": []})
    top = _top_risk(projects)
    if top:
        ml = top["ml"]
        mline = f" The model gives a {ml['slip_prob']:.0%} chance of a revised date being filed next report; top factor: {ml['slip_top_factors'][0]['feature']}." if ml and ml.get("slip_prob") is not None and ml.get("slip_top_factors") else " No model score is attached."
        out.append({"id": 7, "question": f"Why is project {top['project_code']} rated {top['risk']['band']}?",
                    "answer": f"Score {top['risk']['score']:.0f}. " + " ".join(top["risk"]["reasons"][:4]) + mline,
                    "sources": [s for f in top["flags"][:4] for s in f["sources"]]})
    else:
        out.append({"id": 7, "question": "Why is the top project rated as it is?", "answer": "No projects.", "sources": []})
    if models and models["m1_slip"]["results"]:
        res = {r["model_id"]: r for r in models["m1_slip"]["results"] if r["test_pair"] == models["meta"]["test_pair"]}
        hb, lr = res.get("HGB_B"), res.get("LR_A")
        out.append({"id": 8, "question": "Did the model beat the conventional method on the held-out report?",
                    "answer": (f"On pair {models['meta']['test_pair']} (n={hb['n']}, positives={hb['positives']}), gradient boosting with audit features recalled {hb['recall_at_100']:.0%} of the projects that filed a revised date in its top 100 (precision {hb['precision_at_100']:.0%}); logistic regression recalled {lr['recall_at_100']:.0%} (precision {lr['precision_at_100']:.0%}). " + ("The ML model wins." if hb["pr_auc"] > lr["pr_auc"] else "The conventional model wins on PR-AUC; we show it.")) if hb and lr else "Model results incomplete.",
                    "sources": []})
    else:
        out.append({"id": 8, "question": "Did the model beat the conventional method on the held-out report?", "answer": "Models were not run in this build.", "sources": []})
    return out
```

- [x] **Step 4: Write `findings/run.py`**

```python
"""Assemble every JSON the dashboard reads. Usage:
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json [--no-models]"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")  # before any sklearn import (Task 14)
import argparse
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from findings import assistant, contradictions, disclosure_lag, early_warning, exits, field_audit, risk
from findings.panel import latest, load_panel, sector_map, series, snapshots_present, source

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VERSION = "1.0.0"
ARITH = {"EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL"}
run_models = None  # Task 14 assigns findings.models.pipeline.run here


def _round(x):
    if isinstance(x, dict):
        return {k: _round(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_round(v) for v in x]
    if isinstance(x, float):
        return None if math.isnan(x) or math.isinf(x) else round(x, 4)
    return x


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_round(obj), sort_keys=True, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def generated_at():
    return os.environ.get("AGRIM_GENERATED_AT") or datetime.now(timezone.utc).isoformat(timespec="seconds")


def _strip(flag):
    return {k: v for k, v in flag.items() if k != "project_code"}


def build_projects(panel, flags, status, sectors, ml_by_code):
    by_code = {}
    for f in flags:
        by_code.setdefault(f["project_code"], []).append(f)
    projects = []
    for code, rs in series(panel).items():
        fl = by_code.get(code, [])
        projects.append({"project_code": code, "project_name": rs[-1]["project_name"],
                         "agency_raw": next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None),
                         "state": next((r["state"] for r in reversed(rs) if r["state"]), None), "sector": sectors.get(code),
                         "status": status[code][0], "first_seen": status[code][1], "last_seen": status[code][2],
                         "snapshots": [{"snapshot": r["snapshot"], "page": r["page"], "doc_original": r["doc_original"], "doc_revised": r["doc_revised"],
                                        "cost_original_cr": r["cost_original_cr"], "cost_revised_cr": r["cost_revised_cr"],
                                        "expenditure_cum_cr": r["expenditure_cum_cr"], "physical_progress_pct": r["physical_progress_pct"]} for r in rs],
                         "flags": [_strip(f) for f in fl], "risk": risk.score(fl), "ml": (ml_by_code or {}).get(code)})
    return projects


def build_findings(panel, projects, flags, ex, ew, aggregates, models):
    last = latest(panel)
    counts = Counter(panel["snapshot"])
    coverage = []
    for s in snapshots_present(panel):
        printed = ((aggregates or {}).get(s) or {}).get("rows_printed")
        coverage.append({"snapshot": s, "rows_parsed": int(counts[s]), "rows_printed": printed, "pct": round(100 * counts[s] / printed, 2) if printed else None})
    latest_rows = [p["snapshots"][-1] for p in projects if p["last_seen"] == last]
    cost_rev = sum(r["cost_revised_cr"] or 0 for r in latest_rows)
    overrun = sum((r["cost_revised_cr"] - r["cost_original_cr"]) for r in latest_rows if r["cost_revised_cr"] is not None and r["cost_original_cr"] is not None)
    c_rows = [f for f in flags if f["type"] in ARITH or f["type"] == "STAT_ANOMALY"]
    by = {p["project_code"]: p for p in projects}
    contradiction_rows = [{"project_code": f["project_code"], "project_name": by[f["project_code"]]["project_name"], **_strip(f)} for f in c_rows]
    by_type = Counter(f["type"] for f in c_rows)
    groups = {"state": {}, "sector": {}}
    for p in projects:
        if p["last_seen"] != last:
            continue
        for kind, key in [("state", p["state"] or "UNKNOWN"), ("sector", p["sector"] or "UNKNOWN")]:
            g = groups[kind].setdefault(key, {"key": key, "projects": 0, "flagged": 0, "red": 0})
            g["projects"] += 1
            g["flagged"] += 1 if any(f["severity"] != "info" for f in p["flags"]) else 0
            g["red"] += 1 if p["risk"]["band"] == "red" else 0
    watch = {w["project_code"] for w in models["m1_slip"]["watchlist"]} if models else set()
    review = []
    for p in projects:
        if p["last_seen"] != last:
            continue
        if not (any(f["severity"] != "info" for f in p["flags"]) or p["project_code"] in watch):
            continue
        ml = p["ml"] or {}
        review.append({"project_code": p["project_code"], "project_name": p["project_name"], "state": p["state"], "sector": p["sector"],
                       "risk_band": p["risk"]["band"], "risk_score": p["risk"]["score"], "slip_prob": ml.get("slip_prob"),
                       "expected_delay_months": ml.get("expected_delay_months"),
                       "flag_types": ";".join(sorted({f["type"] for f in p["flags"] if f["severity"] != "info"})), "page": p["snapshots"][-1]["page"]})
    review.sort(key=lambda r: (-r["risk_score"], r["project_code"]))
    findings = {
        "meta": {"contract_version": CONTRACT_VERSION, "generated_at": generated_at(), "snapshots": snapshots_present(panel), "coverage": coverage,
                 "headline": {"projects_latest": len(latest_rows), "cost_revised_total_cr": round(cost_rev, 2), "overrun_total_cr": round(overrun, 2),
                              "contradictions_total": len(c_rows), "exits_total": sum(p["exited"] for p in ex["pairs"]),
                              "unreachable_total": sum(1 for f in flags if f["type"] == "DOC_UNREACHABLE"), "watchlist_size": len(watch)}},
        "contradictions": {"by_type": [{"type": t, "count": n} for t, n in sorted(by_type.items())], "rows": contradiction_rows},
        "exits": {"pairs": ex["pairs"], "rows": ex["rows"]},
        "early_warning": {"rows": ew["rows"]},
        "field_audit": field_audit.compute(panel),
        "disclosure_lag": disclosure_lag.compute(panel),
        "by_state": sorted(groups["state"].values(), key=lambda g: g["key"]),
        "by_sector": sorted(groups["sector"].values(), key=lambda g: g["key"]),
        "review_pack": review,
        "assistant": [],
    }
    findings["assistant"] = assistant.build(findings, projects, models)
    return findings


def build(panel, aggregates, with_models):
    flags = contradictions.detect(panel)
    ew = early_warning.compute(panel)
    flags = sorted(flags + ew["flags"], key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    ex = exits.compute(panel, aggregates)
    sectors = sector_map(panel)
    models = model_card = ml_by_code = None
    if with_models:
        if run_models is None:
            raise SystemExit("models are not wired yet (Task 14); run with --no-models")
        models, ml_by_code, extra_flags, model_card = run_models(panel, flags, sectors)
        flags = sorted(flags + extra_flags, key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    projects = build_projects(panel, flags, ex["status"], sectors, ml_by_code)
    findings = build_findings(panel, projects, flags, ex, ew, aggregates, models)
    return projects, findings, models, model_card


def deck_numbers(findings, models):
    h = findings["meta"]["headline"]
    nums = {"projects_latest": h["projects_latest"], "cost_revised_total_cr": h["cost_revised_total_cr"], "overrun_total_cr": h["overrun_total_cr"],
            "contradictions_total": h["contradictions_total"], "exits_total": h["exits_total"], "unreachable_total": h["unreachable_total"],
            "latest_snapshot": findings["meta"]["snapshots"][-1]}
    for c in findings["meta"]["coverage"]:
        if c["pct"] is not None:
            nums[f"coverage_pct_{c['snapshot']}"] = c["pct"]
    for t in findings["contradictions"]["by_type"]:
        nums[f"count_{t['type']}"] = t["count"]
    drops = [r for r in findings["contradictions"]["rows"] if r["type"] == "EXP_DECREASE"
             and isinstance(r["before"], (int, float)) and isinstance(r["after"], (int, float))]
    if drops:
        top = max(drops, key=lambda r: (r["before"] - r["after"], r["project_code"]))
        nums["opener_code"], nums["opener_before_cr"], nums["opener_after_cr"] = top["project_code"], top["before"], top["after"]
    if models:
        for r in models["m1_slip"]["results"]:
            if r["test_pair"] == models["meta"]["test_pair"]:
                for k in ["pr_auc", "precision_at_100", "recall_at_100", "positives", "n"]:
                    nums[f"m1_{r['model_id']}_{k}"] = r[k]
        for r in models["m2_progress"]["results"]:
            nums[f"m2_{r['model_id']}_mae"] = r["mae"]
    return nums


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(ROOT / "data" / "out" / "panel.csv"))
    ap.add_argument("--out", default=str(ROOT / "web" / "public" / "data"))
    ap.add_argument("--deck", default=None)
    ap.add_argument("--aggregates", default=str(ROOT / "data" / "aggregates.json"))
    ap.add_argument("--no-models", action="store_true")
    a = ap.parse_args(argv)
    aggregates = json.loads(Path(a.aggregates).read_text(encoding="utf-8")) if Path(a.aggregates).exists() else {}
    panel = load_panel(a.panel)
    projects, findings, models, model_card = build(panel, aggregates, with_models=not a.no_models)
    out = Path(a.out)
    write_json(out / "projects.json", projects)
    write_json(out / "findings.json", findings)
    if models is not None:
        write_json(out / "models.json", models)
        write_json(out / "model_card.json", model_card)
    if a.deck:
        write_json(a.deck, deck_numbers(findings, models))
    h = findings["meta"]["headline"]
    print(f"wrote {out}: {len(projects)} projects, {h['contradictions_total']} contradictions, {h['exits_total']} exits, {h['unreachable_total']} unreachable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 5: Run the test, then generate and inspect the goldens**

Run: `pytest tests/findings/test_run_fixture.py -q` → Expected: 2 passed.

Run:
```powershell
$env:AGRIM_GENERATED_AT = "fixture"
python -m findings.run --panel contracts/fixtures/panel.sample.csv --out data/out/tmp_golden --no-models
Copy-Item data/out/tmp_golden/projects.json contracts/fixtures/projects.sample.json
Copy-Item data/out/tmp_golden/findings.json contracts/fixtures/findings.sample.json
Remove-Item Env:AGRIM_GENERATED_AT
```
Open `contracts/fixtures/findings.sample.json` and check by eye: `contradictions.rows` contains 100002's EXP_DECREASE with pages 56 and 57; `exits.rows` has 100007 and 100008; `early_warning.rows` has 100006 first. Add the line `- 2026-09-07 v1.0.0 — golden fixtures projects.sample.json / findings.sample.json committed (Task 9).` to `contracts/CHANGELOG.md`.

- [x] **Step 6: Run on the real panel and commit the outputs**

Run:
```powershell
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json --no-models
python tools/validate.py
```
Expected: `wrote web\public\data: N projects, C contradictions, E exits, U unreachable`; validator shows `ok   projects: valid`, `ok   findings: valid`, `ok   golden ... matches`, `ok   deck/numbers.json all traceable`, `RESULT: PASS`.

Open `web/public/data/findings.json` and read `contradictions.rows` filtered to `EXP_DECREASE`: confirm project 705526 appears (cumulative expenditure 53,629.73 → 401.84 between 2025-12 and 2026-04) and note its pages. If it is absent, the parser missed that row: record it in the PR and continue; do not edit data by hand.

- [x] **Step 7: Write `tools/render_pages.py` and render the flagged pages**

```python
"""Render every PDF page cited by a non-info flag to web/public/pages/<snapshot>/p<page>.png (PyMuPDF, 1.5x zoom)."""
import json
from pathlib import Path

import fitz

from tools.fetch_pdfs import PDFS

ROOT = Path(__file__).resolve().parents[1]


def cited_pages(findings_path):
    f = json.loads(Path(findings_path).read_text(encoding="utf-8"))
    pages = set()
    for r in f["contradictions"]["rows"] + f["early_warning"]["rows"] + f["exits"]["rows"]:
        for s in r["sources"]:
            pages.add((s["snapshot"], s["page"]))
    return sorted(pages)


def render(pages, out_dir=ROOT / "web" / "public" / "pages"):
    docs = {}
    n = 0
    for snap, page in pages:
        pdf = ROOT / "data" / "pdfs" / PDFS[snap][0]
        if not pdf.exists():
            continue
        doc = docs.setdefault(snap, fitz.open(pdf))
        dest = out_dir / snap / f"p{page}.png"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(dest)
        n += 1
    return n


if __name__ == "__main__":
    pages = cited_pages(ROOT / "web" / "public" / "data" / "findings.json")
    print("cited pages:", len(pages), "rendered new:", render(pages))
```

Run: `python tools/render_pages.py` → Expected: `cited pages: N rendered new: N` (a few hundred PNGs at most, ~150 KB each).

- [x] **Step 8: Gate and commit**

Run: `pytest -q` and `python tools/validate.py` → all green.

```powershell
git switch -c task/09-assemble
git add -A
git commit -m "task 09: assemble projects.json/findings.json, assistant, review pack, goldens, page renders"
git push -u origin task/09-assemble
gh pr create --title "Task 09: audit layer assembled on real data" --body "<paste validate output and the headline line; note whether 705526 is present>"
```

**Contract freeze is now in effect** (only additive nullable fields from here, logged in `contracts/CHANGELOG.md`).

---

### Task 10: The one feature builder (sets A and B) with a leakage guard

**Files:**
- Create: `findings/features.py`
- Test: `tests/models/conftest.py`, `tests/models/test_features.py`

**Interfaces:**
- Consumes: Tasks 6–8 (`panel`, `early_warning.velocity`, `early_warning.doc_current`).
- Produces: `findings.features.FEATURES_A`, `FEATURES_B`, `CATEGORICAL`; `slip_labels(ser, t0, t1) -> dict[str, int]`; `pair_frame(panel, t0, t1, flags=None) -> pandas.DataFrame` (index `project_code`; columns `FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]`); `snapshot_frame(panel, t, flags=None, gap_months=1) -> DataFrame` (columns `FEATURES_B`); `censored_exits(panel, t0, t1) -> int`; `to_matrix(frames: list[DataFrame], columns: list[str]) -> (list[DataFrame], cat_mask: list[bool])` (categoricals as integer codes from the first frame's categories, unknown → NaN).

- [x] **Step 1: Write the shared test fixture and the failing tests**

Create `tests/models/conftest.py`:
```python
import pytest

from contracts.fixtures.synthetic_panel import write
from findings.panel import load_panel


@pytest.fixture(scope="session")
def synth_path(tmp_path_factory):
    return write(tmp_path_factory.mktemp("synth") / "panel.csv", n_projects=600, seed=0)


@pytest.fixture(scope="session")
def synth(synth_path):
    return load_panel(synth_path)
```
(`contracts/` needs an empty `contracts/__init__.py` and `contracts/fixtures/__init__.py` for this import — create both; they are not schema changes.)

Create `tests/models/test_features.py`:
```python
import math

import pandas as pd

from findings.contradictions import detect
from findings.features import CATEGORICAL, FEATURES_A, FEATURES_B, censored_exits, pair_frame, slip_labels, snapshot_frame, to_matrix
from findings.panel import load_panel, series

FIX = "contracts/fixtures/panel.sample.csv"


def test_labels_and_shapes_on_fixture():
    panel = load_panel(FIX)
    y = slip_labels(series(panel), "2026-04", "2026-05")
    assert y["100006"] == 1 and y["100001"] == 0 and "100008" not in y      # 100008 exits after April
    df = pair_frame(panel, "2026-04", "2026-05", detect(panel))
    assert list(df.columns) == FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]
    assert df.loc["100006", "y_slip"] == 1 and df.loc["100006", "gap_months"] == 1.0
    assert df.loc["100002", "exp_decrease_ever"] == 0.0      # the drop happens in May, after t0 = April
    assert math.isnan(df.loc["100001", "agency_prior_slip_rate"]) is False   # P1 exists before April
    p1 = pair_frame(panel, "2025-12", "2026-04")
    assert all(math.isnan(v) for v in p1["agency_prior_slip_rate"]) and all(math.isnan(v) for v in p1["n_prior_revisions"])
    assert censored_exits(panel, "2026-04", "2026-05") == 1


def test_snapshot_frame_and_matrix(synth):
    sf = snapshot_frame(synth, "2026-07")
    assert list(sf.columns) == FEATURES_B and len(sf) > 400
    (m,), mask = to_matrix([sf], FEATURES_B)
    assert mask == [c in CATEGORICAL for c in FEATURES_B]
    assert m.dtypes.map(lambda d: d.kind).isin(["f", "i"]).all()


def test_no_feature_uses_the_later_month(synth):
    base = pair_frame(synth, "2026-06", "2026-07")
    mutated = synth.copy()
    m = mutated["snapshot"] == "2026-07"
    mutated.loc[m, "physical_progress_pct"] = 0.0
    mutated.loc[m, "expenditure_cum_cr"] = 0.0
    mutated.loc[m, "doc_revised"] = "2099-01"
    mutated.loc[m, "cost_revised_cr"] = 1.0
    after = pair_frame(mutated, "2026-06", "2026-07")
    pd.testing.assert_frame_equal(base[FEATURES_B], after[FEATURES_B])
    assert (base["y_slip"] != after["y_slip"]).any()
```

- [x] **Step 2: Run to verify failure**

Run: `pytest tests/models -q` → Expected: import error for `findings.features`.

- [x] **Step 3: Write `findings/features.py`**

```python
"""The ONE feature builder. Every model imports from here. Features use only snapshots <= t0 (tested)."""
import math
from collections import defaultdict

import numpy as np
import pandas as pd

from findings.early_warning import doc_current, velocity
from findings.panel import ORDER, months, pairs_present, sector_map, series, snapshots_present

FEATURES_A = ["physical_progress_pct", "exp_share", "age_months", "months_to_doc", "log_cost_original", "cost_overrun_pct",
              "time_overrun_months", "has_revised_doc", "sector", "state", "gap_months"]
FEATURES_B = FEATURES_A + ["velocity_pct_per_month", "unreachable_ratio", "n_prior_revisions", "agency_prior_slip_rate",
                           "n_flags_to_t0", "exp_decrease_ever"]
CATEGORICAL = ["sector", "state"]
ARITH = {"EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL"}
NAN = float("nan")


def slip_labels(ser, t0, t1):
    out = {}
    for code, rs in ser.items():
        d = {r["snapshot"]: r for r in rs}
        if t0 in d and t1 in d:
            out[code] = int(d[t0]["doc_revised"] != d[t1]["doc_revised"])
    return out


def censored_exits(panel, t0, t1):
    ser = series(panel)
    a = {c for c, rs in ser.items() if any(r["snapshot"] == t0 for r in rs)}
    b = {c for c, rs in ser.items() if any(r["snapshot"] == t1 for r in rs)}
    return len(a - b)


def _upto(rs, t0):
    return [r for r in rs if ORDER[r["snapshot"]] <= ORDER[t0]]


def _ratio(rs_upto):
    last = rs_upto[-1]
    prog, doc = last["physical_progress_pct"], doc_current(last)
    v = velocity(rs_upto)
    if prog is None or prog >= 100 or doc is None or v is None or v <= 0:
        return NAN
    rem = months(last["snapshot"], doc)
    return ((100 - prog) / v) / rem if rem > 0 else NAN


def _set_a(rs_upto, sector, gap):
    last = rs_upto[-1]
    t0 = last["snapshot"]
    prog, co, cr, exp = last["physical_progress_pct"], last["cost_original_cr"], last["cost_revised_cr"], last["expenditure_cum_cr"]
    doc = doc_current(last)
    return {
        "physical_progress_pct": NAN if prog is None else float(prog),
        "exp_share": exp / cr if exp is not None and cr else NAN,
        "age_months": float(months(last["approval_month"], t0)) if last["approval_month"] else NAN,
        "months_to_doc": float(months(t0, doc)) if doc else NAN,
        "log_cost_original": math.log(co + 1) if co is not None else NAN,
        "cost_overrun_pct": (cr - co) / co * 100 if co and cr is not None else NAN,
        "time_overrun_months": float(months(last["doc_original"], last["doc_revised"])) if last["doc_original"] and last["doc_revised"]
                               else (0.0 if last["doc_original"] else NAN),
        "has_revised_doc": 1.0 if last["doc_revised"] else 0.0,
        "sector": sector or "UNKNOWN", "state": last["state"] or "UNKNOWN", "gap_months": float(gap),
    }


def _history(panel, ser, t0, flags):
    """Per-code history features from pairs whose later month is <= t0 (strictly before the pair being built)."""
    earlier = [(a, b) for _, a, b in pairs_present(panel) if ORDER[b] <= ORDER[t0]]
    labels = [slip_labels(ser, a, b) for a, b in earlier]
    agency_of = {c: next((r["agency_raw"] for r in reversed(rs) if r["agency_raw"]), None) for c, rs in ser.items()}
    prior_revs, acc = defaultdict(int), defaultdict(list)
    for lab in labels:
        for c, y in lab.items():
            prior_revs[c] += y
            acc[agency_of[c]].append(y)
    agency_rate = {ag: sum(v) / len(v) for ag, v in acc.items()}
    nflags, expdec = defaultdict(int), defaultdict(int)
    for f in flags or []:
        if ORDER[f["to_snapshot"]] <= ORDER[t0]:
            if f["type"] in ARITH:
                nflags[f["project_code"]] += 1
            if f["type"] == "EXP_DECREASE":
                expdec[f["project_code"]] = 1

    def for_code(code, rs_upto):
        return {"velocity_pct_per_month": velocity(rs_upto) if velocity(rs_upto) is not None else NAN,
                "unreachable_ratio": _ratio(rs_upto),
                "n_prior_revisions": float(prior_revs[code]) if earlier else NAN,
                "agency_prior_slip_rate": agency_rate.get(agency_of[code], NAN) if earlier else NAN,
                "n_flags_to_t0": float(nflags[code]), "exp_decrease_ever": float(expdec[code])}
    return for_code


def _frame(rows_by_code):
    df = pd.DataFrame.from_dict(rows_by_code, orient="index")
    df.index.name = "project_code"
    for c in CATEGORICAL:
        df[c] = df[c].astype("category")
    return df


def pair_frame(panel, t0, t1, flags=None):
    ser, sectors = series(panel), sector_map(panel)
    gap = months(t0, t1)
    hist = _history(panel, ser, t0, flags)
    y = slip_labels(ser, t0, t1)
    rows = {}
    for code in sorted(y):
        rs = ser[code]
        up = _upto(rs, t0)
        r1 = next(r for r in rs if r["snapshot"] == t1)
        p0, p1 = up[-1]["physical_progress_pct"], r1["physical_progress_pct"]
        feat = {**_set_a(up, sectors.get(code), gap), **hist(code, up)}
        feat["y_slip"] = y[code]
        feat["delta_prog"] = (p1 - p0) if p0 is not None and p1 is not None else NAN
        feat["prog_t1"] = NAN if p1 is None else float(p1)
        rows[code] = feat
    return _frame(rows)[FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]]


def snapshot_frame(panel, t, flags=None, gap_months=1):
    ser, sectors = series(panel), sector_map(panel)
    hist = _history(panel, ser, t, flags)
    rows = {}
    for code, rs in ser.items():
        if not any(r["snapshot"] == t for r in rs):
            continue
        up = _upto(rs, t)
        rows[code] = {**_set_a(up, sectors.get(code), gap_months), **hist(code, up)}
    return _frame(rows)[FEATURES_B]


def to_matrix(frames, columns):
    """Categoricals -> integer codes using the FIRST frame's categories (unknown -> NaN); numerics unchanged."""
    cats = {c: list(frames[0][c].astype(str).unique()) for c in columns if c in CATEGORICAL}
    out = []
    for df in frames:
        m = df[columns].copy()
        for c, levels in cats.items():
            idx = {v: i for i, v in enumerate(levels)}
            m[c] = m[c].astype(str).map(idx).astype(float)
        out.append(m.astype(float))
    return out, [c in CATEGORICAL for c in columns]
```

- [x] **Step 4: Run tests, gate, commit**

Run: `pytest tests/models -q` → 3 passed. `python tools/validate.py` → PASS.

```powershell
git switch -c task/10-features
git add -A
git commit -m "task 10: single feature builder with sets A/B and leakage guard"
git push -u origin task/10-features
gh pr create --title "Task 10: feature builder" --body "<paste outputs>"
```

---

### Task 11: M1 slip-filing classifier (gradient boosting vs logistic regression, sets A vs B)

**Files:**
- Create: `findings/models/metrics.py`, `findings/models/m1_slip.py`
- Test: `tests/models/test_m1.py`

**Interfaces:**
- Consumes: Task 10.
- Produces: `findings.models.metrics.summarize(model_id, test_pair, y, s) -> dict` (one `m1_slip.results` row); `findings.models.m1_slip.run(panel, flags, frames: dict[str, DataFrame], pair_list: list[tuple], test_pair="P4") -> (m1_json: dict, per_project: dict[str, dict], pairs_meta: list[dict])` where `per_project[code] = {"slip_prob", "slip_rank", "slip_top_factors"}` for every project present at the latest snapshot.

- [x] **Step 1: Write the failing test**

Create `tests/models/test_m1.py`:
```python
import json

from findings.contradictions import detect
from findings.features import pair_frame
from findings.models.m1_slip import run
from findings.panel import pairs_present


def frames_for(panel):
    flags = detect(panel)
    pairs = pairs_present(panel)
    return flags, {pid: pair_frame(panel, a, b, flags) for pid, a, b in pairs}, pairs


def test_m1_beats_base_rate_and_shuffle_and_is_deterministic(synth):
    flags, frames, pairs = frames_for(synth)
    m1, per_project, meta = run(synth, flags, frames, pairs, test_pair="P4")
    res = {r["model_id"]: r for r in m1["results"] if r["test_pair"] == "P4"}
    assert set(res) == {"LR_A", "HGB_A", "HGB_B", "HGB_B_SHUFFLED"}
    assert res["HGB_B"]["positives"] >= 20
    assert res["HGB_B"]["pr_auc"] > 1.5 * res["HGB_B"]["base_rate"]
    assert res["HGB_B"]["pr_auc"] > res["HGB_B_SHUFFLED"]["pr_auc"]
    assert abs(res["HGB_B_SHUFFLED"]["pr_auc"] - res["HGB_B_SHUFFLED"]["base_rate"]) < 0.08
    assert 0 <= res["HGB_B"]["recall_at_100"] <= 1 and len(res["HGB_B"]["calibration"]) == 10
    assert len(m1["watchlist"]) == 100 and m1["watchlist"][0]["slip_rank"] == 1
    assert len(m1["importance_HGB_B"]) == len(m1["feature_sets"]["B"])
    p = per_project[m1["watchlist"][0]["project_code"]]
    assert set(p) == {"slip_prob", "slip_rank", "slip_top_factors"} and len(p["slip_top_factors"]) == 5
    assert [x["id"] for x in meta] == ["P1", "P2", "P3", "P4"] and all(x["n"] > 0 for x in meta)
    m1b, _, _ = run(synth, flags, frames, pairs, test_pair="P4")
    assert json.dumps(m1, sort_keys=True) == json.dumps(m1b, sort_keys=True)
```

- [x] **Step 2: Run to verify failure**

Run: `pytest tests/models/test_m1.py -q` → Expected: import error.

- [x] **Step 3: Write `findings/models/metrics.py`**

```python
"""Ranking metrics for an officer's decision: which 100 projects to review this month. No accuracy, ever."""
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score


def _order(s):
    return np.argsort(-np.asarray(s), kind="stable")


def precision_at_k(y, s, k=100):
    top = np.asarray(y)[_order(s)[:k]]
    return float(top.mean()) if len(top) else 0.0


def recall_at_k(y, s, k=100):
    y = np.asarray(y)
    pos = y.sum()
    return float(y[_order(s)[:k]].sum() / pos) if pos else 0.0


def calibration(y, s, bins=10):
    y, s = np.asarray(y), np.asarray(s)
    edges = np.linspace(0, 1, bins + 1)
    out = []
    for i in range(bins):
        m = (s >= edges[i]) & ((s < edges[i + 1]) if i < bins - 1 else (s <= edges[i + 1]))
        out.append({"bin": i, "mean_pred": float(s[m].mean()) if m.any() else None,
                    "mean_obs": float(y[m].mean()) if m.any() else None, "n": int(m.sum())})
    return out


def pr_curve_points(y, s, n=50):
    p, r, _ = precision_recall_curve(y, s)
    idx = np.linspace(0, len(p) - 1, min(n, len(p))).astype(int)
    return [{"x": float(r[i]), "y": float(p[i])} for i in idx]


def summarize(model_id, test_pair, y, s):
    y, s = np.asarray(y).astype(int), np.asarray(s, dtype=float)
    positives, n = int(y.sum()), int(len(y))
    base = positives / n if n else 0.0
    p100 = precision_at_k(y, s)
    return {"model_id": model_id, "test_pair": test_pair, "n": n, "positives": positives, "base_rate": base,
            "pr_auc": float(average_precision_score(y, s)) if 0 < positives < n else 0.0,
            "roc_auc": float(roc_auc_score(y, s)) if 0 < positives < n else None,
            "precision_at_100": p100, "recall_at_100": recall_at_k(y, s),
            "lift_at_100": (p100 / base) if base else None,
            "calibration": calibration(y, s), "pr_curve": pr_curve_points(y, s) if 0 < positives < n else []}
```

- [x] **Step 4: Write `findings/models/m1_slip.py`**

```python
"""M1: will this project file a revised completion date in the next report? Out-of-time validation; baseline always shown."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from findings.features import CATEGORICAL, FEATURES_A, FEATURES_B, censored_exits, snapshot_frame, to_matrix
from findings.models.metrics import summarize
from findings.panel import latest, months

SEED = 0
HGB = dict(max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.15, class_weight="balanced", random_state=SEED)


def fit_hgb(X, y, cat_mask):
    return HistGradientBoostingClassifier(categorical_features=cat_mask, **HGB).fit(X, y)


def fit_lr(df, y):
    cats = [c for c in df.columns if c in CATEGORICAL]
    nums = [c for c in df.columns if c not in CATEGORICAL]
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), cats),
                              ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), nums)])
    pipe = Pipeline([("prep", prep), ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=SEED))])
    return pipe.fit(df.assign(**{c: df[c].astype(str) for c in cats}), y)


def _lr_frame(df):
    return df[FEATURES_A].assign(**{c: df[c].astype(str) for c in CATEGORICAL})


def _shap_factors(model, X, raw, k=5):
    try:
        import shap
        sv = shap.TreeExplainer(model).shap_values(X.values)
        if isinstance(sv, list):
            sv = sv[-1]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[..., -1]
    except Exception:  # SHAP unavailable or unsupported: fall back to zero contributions, still deterministic
        sv = np.zeros(X.shape)
    factors = {}
    for i, code in enumerate(X.index):
        order = np.argsort(-np.abs(sv[i]), kind="stable")[:k]
        fs = []
        for j in order:
            col = X.columns[j]
            val = raw.loc[code, col]
            if isinstance(val, float) and np.isnan(val):
                val = None
            elif not isinstance(val, (int, float, str)):
                val = str(val)
            fs.append({"feature": col, "contribution": float(sv[i, j]), "value": val})
        factors[code] = fs
    return factors


def run(panel, flags, frames, pair_list, test_pair="P4"):
    ids = [pid for pid, _, _ in pair_list]
    if test_pair not in frames:
        test_pair = ids[-1]
    train_ids = ids[:ids.index(test_pair)]
    if not train_ids:
        raise SystemExit("M1 needs at least one training pair before the test pair")
    evaluations = [(train_ids, test_pair)]
    if len(train_ids) >= 2:
        evaluations.append((train_ids[:-1], train_ids[-1]))
    results, keep = [], {}
    for tr_ids, te in evaluations:
        tr = pd.concat([frames[i] for i in tr_ids])
        te_df = frames[te]
        y_tr, y_te = tr["y_slip"].values.astype(int), te_df["y_slip"].values.astype(int)
        if y_tr.sum() == 0 or y_te.sum() == 0:
            continue
        lr = fit_lr(_lr_frame(tr), y_tr)
        results.append(summarize("LR_A", te, y_te, lr.predict_proba(_lr_frame(te_df))[:, 1]))
        for mid, cols in [("HGB_A", FEATURES_A), ("HGB_B", FEATURES_B)]:
            (Xtr, Xte), mask = to_matrix([tr, te_df], cols)
            m = fit_hgb(Xtr, y_tr, mask)
            results.append(summarize(mid, te, y_te, m.predict_proba(Xte)[:, 1]))
            if mid == "HGB_B" and te == test_pair:
                keep = {"model": m, "Xte": Xte, "y_te": y_te, "lr": lr}
                ys = np.random.RandomState(SEED).permutation(y_tr)
                results.append(summarize("HGB_B_SHUFFLED", te, y_te, fit_hgb(Xtr, ys, mask).predict_proba(Xte)[:, 1]))
    if not keep:
        raise SystemExit(f"M1: no positives in test pair {test_pair}; cannot evaluate")
    imp = permutation_importance(keep["model"], keep["Xte"], keep["y_te"], scoring="average_precision", n_repeats=10, random_state=SEED)
    importance = sorted([{"feature": f, "mean": float(m), "std": float(s)} for f, m, s in zip(FEATURES_B, imp.importances_mean, imp.importances_std)],
                        key=lambda d: (-d["mean"], d["feature"]))
    names = keep["lr"].named_steps["prep"].get_feature_names_out()
    coefs = [{"feature": str(n), "value": float(c)} for n, c in zip(names, keep["lr"].named_steps["clf"].coef_[0])]
    allf = pd.concat([frames[i] for i in ids])
    last = latest(panel)
    latest_frame = snapshot_frame(panel, last, flags, gap_months=1)
    (Xall, Xlatest), mask = to_matrix([allf, latest_frame], FEATURES_B)
    final = fit_hgb(Xall, allf["y_slip"].values.astype(int), mask)
    probs = final.predict_proba(Xlatest)[:, 1]
    order = sorted(range(len(probs)), key=lambda i: (-probs[i], latest_frame.index[i]))
    rank = {latest_frame.index[i]: r + 1 for r, i in enumerate(order)}
    factors = _shap_factors(final, Xlatest, latest_frame)
    per_project = {code: {"slip_prob": float(probs[i]), "slip_rank": rank[code], "slip_top_factors": factors[code]}
                   for i, code in enumerate(latest_frame.index)}
    watch = [{"project_code": c, "slip_prob": per_project[c]["slip_prob"], "slip_rank": per_project[c]["slip_rank"]}
             for c in sorted(per_project, key=lambda c: per_project[c]["slip_rank"])[:100]]
    pairs_meta = [{"id": pid, "from": a, "to": b, "gap_months": months(a, b), "n": int(len(frames[pid])),
                   "positives": int(frames[pid]["y_slip"].sum()), "censored_exits": censored_exits(panel, a, b)} for pid, a, b in pair_list]
    m1 = {"feature_sets": {"A": FEATURES_A, "B": FEATURES_B}, "results": results, "importance_HGB_B": importance,
          "coefficients_LR_A": coefs, "watchlist": watch}
    return m1, per_project, pairs_meta
```

- [x] **Step 5: Run tests, gate, commit**

Run: `pytest tests/models/test_m1.py -q` → 1 passed (about a minute). If the shuffle assertion fails by a small margin, the synthetic base rate is very low; do not loosen the test — raise `n_projects` in `conftest.py` to 900 and re-run. `python tools/validate.py` → PASS.

```powershell
git switch -c task/11-m1
git add -A
git commit -m "task 11: M1 slip-filing classifier with baselines, shuffle control, SHAP factors, watchlist"
git push -u origin task/11-m1
gh pr create --title "Task 11: M1" --body "<paste outputs>"
```

---

### Task 12: M2 progress forecaster and per-project outlook

**Files:**
- Create: `findings/models/m2_progress.py`
- Test: `tests/models/test_m2.py`

**Interfaces:**
- Consumes: Task 10 frames; Task 7 `early_warning` flags.
- Produces: `findings.models.m2_progress.run(panel, flags, frames, pair_list, test_pair="P4") -> (m2_json, per_project)` with `per_project[code] = {"progress_next_pred", "expected_completion", "expected_delay_months"}` for every project present at the latest snapshot.

- [ ] **Step 1: Write the failing test**

Create `tests/models/test_m2.py`:
```python
from findings.contradictions import detect
from findings.features import pair_frame
from findings.models.m2_progress import run
from findings.panel import pairs_present


def test_m2_baselines_winner_and_outlook(synth):
    flags = detect(synth)
    pairs = pairs_present(synth)
    frames = {pid: pair_frame(synth, a, b, flags) for pid, a, b in pairs}
    m2, per = run(synth, flags, frames, pairs, test_pair="P4")
    ids = {r["model_id"] for r in m2["results"]}
    assert ids == {"ZERO", "OWN_VELOCITY", "HGB"} and m2["winner"] in ids
    assert all(r["mae"] >= 0 and r["n"] > 0 for r in m2["results"])
    assert m2["agreement_with_F3"]["n"] >= 0
    code, p = next(iter(per.items()))
    assert set(p) == {"progress_next_pred", "expected_completion", "expected_delay_months"}
    done = [p for p in per.values() if p["expected_completion"]]
    assert done and all(len(p["expected_completion"]) == 7 for p in done)
    assert any(p["expected_delay_months"] is not None for p in per.values())
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/models/test_m2.py -q` → import error.

- [ ] **Step 3: Write `findings/models/m2_progress.py`**

```python
"""M2: next-month physical progress (points/month) vs no-change and the project's own velocity; then a per-project outlook."""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from findings.early_warning import doc_current
from findings.features import FEATURES_B, snapshot_frame, to_matrix
from findings.panel import add_months, latest, months, series

SEED = 0
MAX_MONTHS = 120
HGB_PARAMS = dict(loss="absolute_error", max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.15, random_state=SEED)


def _own_velocity(df, sector_median):
    v = df["velocity_pct_per_month"].copy()
    fill = df["sector"].astype(str).map(sector_median).astype(float)
    return v.fillna(fill).fillna(float(np.nanmedian(list(sector_median.values())) if sector_median else 0.0)).values


def run(panel, flags, frames, pair_list, test_pair="P4"):
    ids = [pid for pid, _, _ in pair_list]
    if test_pair not in frames:
        test_pair = ids[-1]
    before = ids[:ids.index(test_pair)]
    train_ids = [i for i in before if float(frames[i]["gap_months"].iloc[0]) == 1.0] or before
    tr = pd.concat([frames[i] for i in train_ids]).dropna(subset=["delta_prog"])
    te = frames[test_pair].dropna(subset=["delta_prog", "prog_t1"])
    y_tr = (tr["delta_prog"] / tr["gap_months"]).values
    sector_median = tr.assign(y=y_tr).groupby(tr["sector"].astype(str))["y"].median().to_dict()
    gap_te = te["gap_months"].values
    prog0 = te["physical_progress_pct"].fillna(0).values
    truth = te["prog_t1"].values
    preds = {"ZERO": prog0, "OWN_VELOCITY": np.clip(prog0 + _own_velocity(te, sector_median) * gap_te, 0, 100)}
    (Xtr, Xte), mask = to_matrix([tr, te], FEATURES_B)
    hgb = HistGradientBoostingRegressor(categorical_features=mask, **HGB_PARAMS).fit(Xtr, y_tr)
    preds["HGB"] = np.clip(prog0 + hgb.predict(Xte) * gap_te, 0, 100)
    results = []
    for mid, p in preds.items():
        err = np.abs(p - truth)
        results.append({"model_id": mid, "test_pair": test_pair, "n": int(len(err)), "mae": float(err.mean()), "median_ae": float(np.median(err))})
    winner = min(results, key=lambda r: (r["mae"], r["model_id"]))["model_id"]
    # outlook at the latest snapshot with the winning method
    last = latest(panel)
    lf = snapshot_frame(panel, last, flags, gap_months=1)
    ser = series(panel)
    allf = pd.concat([frames[i] for i in ids]).dropna(subset=["delta_prog"])
    per = {}
    prog = lf["physical_progress_pct"].fillna(0).values.copy()
    if winner == "HGB":
        (Xall, Xl), mask = to_matrix([allf, lf], FEATURES_B)
        model = HistGradientBoostingRegressor(categorical_features=mask, **HGB_PARAMS).fit(Xall, (allf["delta_prog"] / allf["gap_months"]).values)
        Xsim = Xl.copy()
    else:
        vel = _own_velocity(lf, sector_median)
    done = np.full(len(lf), -1)
    first = None
    for k in range(1, MAX_MONTHS + 1):
        if winner == "ZERO":
            break
        if winner == "HGB":
            Xsim["physical_progress_pct"] = prog
            Xsim["age_months"] = Xsim["age_months"] + 1
            Xsim["months_to_doc"] = Xsim["months_to_doc"] - 1
            delta = model.predict(Xsim)
        else:
            delta = vel
        if first is None:
            first = np.clip(prog + delta, 0, 100)
        prog = np.clip(prog + delta, 0, 100)
        newly = (done < 0) & (prog >= 100)
        done[newly] = k
        if (done >= 0).all():
            break
    for i, code in enumerate(lf.index):
        row = ser[code][-1]
        completion = add_months(last, int(done[i])) if done[i] > 0 else None
        doc = doc_current(row)
        per[code] = {"progress_next_pred": float(first[i]) if first is not None else float(prog[i]),
                     "expected_completion": completion,
                     "expected_delay_months": float(months(doc, completion)) if completion and doc else None}
    f3 = {f["project_code"] for f in flags if f["type"] in ("DOC_UNREACHABLE", "DOC_PASSED")}
    both = [c for c in per if c in f3 and per[c]["expected_delay_months"] is not None]
    agree = sum(1 for c in both if per[c]["expected_delay_months"] > 0)
    m2 = {"results": results, "winner": winner,
          "agreement_with_F3": {"n": len(both), "share_same_direction": (agree / len(both)) if both else None}}
    return m2, per
```

- [ ] **Step 4: Run tests, gate, commit**

Run: `pytest tests/models/test_m2.py -q` → 1 passed. `python tools/validate.py` → PASS.

```powershell
git switch -c task/12-m2
git add -A
git commit -m "task 12: M2 progress forecaster vs baselines; per-project outlook"
git push -u origin task/12-m2
gh pr create --title "Task 12: M2" --body "<paste outputs>"
```

---

### Task 13: M3 overrun drivers and peer benchmark; M4 statistical anomalies

**Files:**
- Create: `findings/models/m3_drivers.py`, `findings/models/m4_anomaly.py`
- Test: `tests/models/test_m3_m4.py`

**Interfaces:**
- Consumes: Task 10.
- Produces: `findings.models.m3_drivers.run(panel, flags) -> (m3_json, per_project)` with `per_project[code] = {"peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months"}`; `findings.models.m4_anomaly.run(panel) -> (m4_json, per_project, extra_flags)` with `per_project[code] = {"anomaly_score", "anomaly_flag"}` and `extra_flags` = `STAT_ANOMALY` flag dicts (with `project_code`).

- [ ] **Step 1: Write the failing test**

Create `tests/models/test_m3_m4.py`:
```python
from findings.contradictions import detect
from findings.models.m3_drivers import run as m3
from findings.models.m4_anomaly import run as m4


def test_m3_results_pdp_benchmark(synth):
    out, per = m3(synth, detect(synth))
    assert out["snapshot"] == "2026-07" and out["n"] > 400
    assert {(r["target"], r["model_id"]) for r in out["results"]} == {(t, m) for t in ["cost_overrun_pct", "time_overrun_months"] for m in ["OLS", "HGB"]}
    assert len(out["partial_dependence"]) == 6 and all(len(p["grid"]) == len(p["values"]) for p in out["partial_dependence"])
    assert out["sector_effects"] and any(c["target"] == "cost_overrun_pct" for c in out["coefficients_OLS"])
    p = next(iter(per.values()))
    assert set(p) == {"peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months"}


def test_m4_flags_about_two_percent(synth):
    out, per, flags = m4(synth)
    assert out["contamination"] == "auto" and out["n"] > 1000
    assert 0.01 <= len(out["flagged"]) / out["n"] <= 0.03
    assert all(f["type"] == "STAT_ANOMALY" and f["severity"] == "info" and f["sources"] for f in flags)
    assert any(p["anomaly_flag"] for p in per.values()) and all(p["anomaly_score"] is not None for p in per.values())
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/models/test_m3_m4.py -q` → import error.

- [ ] **Step 3: Write `findings/models/m3_drivers.py`**

```python
"""M3: what drives cost and time overrun across the panel (OLS vs gradient boosting) and how each project compares with its peers."""
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import partial_dependence
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from findings.features import snapshot_frame, to_matrix
from findings.panel import latest, series

SEED = 0
FEATS = ["log_cost_original", "age_months", "physical_progress_pct", "approval_year", "agency_size", "sector", "state"]
CATS = ["sector", "state"]
PDP_FEATS = ["log_cost_original", "age_months", "physical_progress_pct"]
TARGETS = {"cost_overrun_pct": (-50, 500), "time_overrun_months": (0, 240)}


def frame(panel, flags):
    last = latest(panel)
    sf = snapshot_frame(panel, last, flags)
    ser = series(panel)
    rows_last = {c: rs[-1] for c, rs in ser.items() if rs[-1]["snapshot"] == last}
    agency = {c: r["agency_raw"] for c, r in rows_last.items()}
    size = Counter(a for a in agency.values() if a)
    df = sf.copy()
    df["approval_year"] = [float(rows_last[c]["approval_month"][:4]) if rows_last[c]["approval_month"] else np.nan for c in df.index]
    df["agency_size"] = [float(size.get(agency[c], 0)) for c in df.index]
    for t, (lo, hi) in TARGETS.items():
        df[t] = df[t].clip(lo, hi)
    return df[df["log_cost_original"].notna()]


def _ols():
    prep = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CATS),
                              ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), [f for f in FEATS if f not in CATS])])
    return Pipeline([("prep", prep), ("reg", LinearRegression())])


def _str_cats(df):
    return df[FEATS].assign(**{c: df[c].astype(str) for c in CATS})


def run(panel, flags):
    df = frame(panel, flags)
    kf = KFold(5, shuffle=True, random_state=SEED)
    results, pdps, coefs, per = [], [], [], {c: {} for c in df.index}
    sector_eff = {}
    for target in TARGETS:
        d = df.dropna(subset=[target])
        y = d[target].values
        Xs = _str_cats(d)
        ols = _ols()
        results.append({"target": target, "model_id": "OLS", "cv_r2": float(cross_val_score(ols, Xs, y, cv=kf, scoring="r2").mean()),
                        "cv_mae": float(-cross_val_score(ols, Xs, y, cv=kf, scoring="neg_mean_absolute_error").mean())})
        ols.fit(Xs, y)
        names = ols.named_steps["prep"].get_feature_names_out()
        for n, c in zip(names, ols.named_steps["reg"].coef_):
            coefs.append({"target": target, "feature": str(n), "coef": float(c)})
            if str(n).startswith("cat__sector_"):
                sector_eff.setdefault(str(n)[len("cat__sector_"):], {})[target] = float(c)
        (X,), mask = to_matrix([d], FEATS)
        hgb = HistGradientBoostingRegressor(categorical_features=mask, random_state=SEED)
        results.append({"target": target, "model_id": "HGB", "cv_r2": float(cross_val_score(hgb, X, y, cv=kf, scoring="r2").mean()),
                        "cv_mae": float(-cross_val_score(hgb, X, y, cv=kf, scoring="neg_mean_absolute_error").mean())})
        expected = cross_val_predict(hgb, X, y, cv=kf)
        hgb.fit(X, y)
        for f in PDP_FEATS:
            pd_res = partial_dependence(hgb, X, [FEATS.index(f)], grid_resolution=20, kind="average")
            grid = pd_res["grid_values"][0] if "grid_values" in pd_res else pd_res["values"][0]
            pdps.append({"target": target, "feature": f, "grid": [float(g) for g in grid], "values": [float(v) for v in pd_res["average"][0]]})
        key_e, key_r = ("peer_expected_cost_overrun_pct", "cost_overrun_residual_pct") if target == "cost_overrun_pct" else ("peer_expected_time_overrun_months", "time_overrun_residual_months")
        for code, e, a in zip(d.index, expected, y):
            per[code][key_e], per[code][key_r] = float(e), float(a - e)
    for code in per:
        for k in ["peer_expected_cost_overrun_pct", "cost_overrun_residual_pct", "peer_expected_time_overrun_months", "time_overrun_residual_months"]:
            per[code].setdefault(k, None)
    counts = Counter(df["sector"].astype(str))
    effects = [{"sector": s, "effect_cost_pct": v.get("cost_overrun_pct", 0.0), "effect_time_months": v.get("time_overrun_months", 0.0), "n": int(counts.get(s, 0))}
               for s, v in sorted(sector_eff.items())]
    return {"snapshot": latest(panel), "n": int(len(df)), "results": results, "partial_dependence": pdps,
            "sector_effects": effects, "coefficients_OLS": coefs}, per
```

- [ ] **Step 4: Write `findings/models/m4_anomaly.py`**

```python
"""M4: month-to-month changes that are unusual even when arithmetically possible. Never re-labels F1's impossibilities."""
import math

import numpy as np
from sklearn.ensemble import IsolationForest

from findings.panel import months, pairs_present, series, source

SEED = 0
SHARE = 0.02


def _feat(a, b):
    def d(k):
        return (b[k] - a[k]) if a[k] is not None and b[k] is not None else 0.0
    cr = a["cost_revised_cr"] or 0.0
    return [d("expenditure_cum_cr"), d("expenditure_cum_cr") / cr if cr else 0.0, d("physical_progress_pct"), d("cost_revised_cr"),
            float(months(a["snapshot"], b["snapshot"])), a["physical_progress_pct"] if a["physical_progress_pct"] is not None else 50.0]


def run(panel):
    ser = series(panel)
    rows, meta = [], []
    for pid, t0, t1 in pairs_present(panel):
        for code, rs in ser.items():
            d = {r["snapshot"]: r for r in rs}
            if t0 in d and t1 in d:
                rows.append(_feat(d[t0], d[t1]))
                meta.append((pid, code, d[t0], d[t1]))
    X = np.asarray(rows, dtype=float)
    scores = -IsolationForest(contamination="auto", random_state=SEED).fit(X).score_samples(X)
    flagged, extra, per = [], [], {}
    for pid in sorted({m[0] for m in meta}):
        idx = [i for i, m in enumerate(meta) if m[0] == pid]
        k = max(1, math.ceil(SHARE * len(idx)))
        top = sorted(idx, key=lambda i: (-scores[i], meta[i][1]))[:k]
        for i in top:
            _, code, a, b = meta[i]
            src = [source(a), source(b)]
            flagged.append({"project_code": code, "pair": pid, "score": float(scores[i]), "sources": src})
            extra.append({"project_code": code, "type": "STAT_ANOMALY", "severity": "info", "from_snapshot": a["snapshot"], "to_snapshot": b["snapshot"],
                          "before": a["expenditure_cum_cr"], "after": b["expenditure_cum_cr"],
                          "detail": f"Month-to-month change between {a['snapshot']} and {b['snapshot']} is in the top {int(SHARE * 100)}% most unusual for that pair (isolation score {scores[i]:.3f}).",
                          "sources": src})
    flagged_codes = {f["project_code"] for f in flagged}
    for i, (pid, code, a, b) in enumerate(meta):
        p = per.setdefault(code, {"anomaly_score": 0.0, "anomaly_flag": code in flagged_codes})
        p["anomaly_score"] = max(p["anomaly_score"], float(scores[i]))
    flagged.sort(key=lambda f: (f["pair"], -f["score"], f["project_code"]))
    extra.sort(key=lambda f: (f["project_code"], f["to_snapshot"], f["type"]))
    return {"n": int(len(rows)), "contamination": "auto", "flagged": flagged}, per, extra
```

- [ ] **Step 5: Run tests, gate, commit**

Run: `pytest tests/models/test_m3_m4.py -q` → 2 passed. `python tools/validate.py` → PASS.

```powershell
git switch -c task/13-m3-m4
git add -A
git commit -m "task 13: M3 overrun drivers and peer benchmark; M4 isolation-forest anomalies"
git push -u origin task/13-m3-m4
gh pr create --title "Task 13: M3 and M4" --body "<paste outputs>"
```

---

### Task 14: Wire the models into the pipeline, model card, full real-data run

**Files:**
- Create: `findings/models/pipeline.py`, `findings/models/model_card.py`, `web/public/data/models.json`, `web/public/data/model_card.json` (generated, committed)
- Modify: `findings/run.py` (two lines: import and `run_models` assignment), `web/public/data/projects.json`, `findings.json`, `deck/numbers.json` (regenerated with models)
- Test: `tests/models/test_pipeline.py`

**Interfaces:**
- Consumes: Tasks 9–13.
- Produces: `findings.models.pipeline.run(panel, flags, sectors) -> (models_json, ml_by_code, extra_flags, model_card)`; `findings.models.model_card.build(models_json, panel) -> dict`. After this task `python -m findings.run` (without `--no-models`) writes all five JSON files.

- [ ] **Step 1: Write the failing test**

Create `tests/models/test_pipeline.py`:
```python
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def run(panel_path, out):
    env = {**os.environ, "AGRIM_GENERATED_AT": "test", "OMP_NUM_THREADS": "1"}
    p = subprocess.run([sys.executable, "-m", "findings.run", "--panel", str(panel_path), "--out", str(out), "--deck", str(out / "numbers.json")],
                       capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stdout + p.stderr


def test_full_pipeline_on_synthetic_validates_and_is_deterministic(synth_path, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    run(synth_path, a)
    run(synth_path, b)
    for name in ["projects", "findings", "models", "model_card"]:
        schema = json.loads(Path(f"contracts/{name}.schema.json").read_text(encoding="utf-8"))
        data = json.loads((a / f"{name}.json").read_text(encoding="utf-8"))
        assert list(Draft202012Validator(schema).iter_errors(data)) == [], name
        assert (a / f"{name}.json").read_bytes() == (b / f"{name}.json").read_bytes(), f"{name} not deterministic"
    projects = json.loads((a / "projects.json").read_text(encoding="utf-8"))
    ongoing = [p for p in projects if p["status"] == "ongoing"]
    assert all(p["ml"] is not None and p["ml"]["scored_at_snapshot"] == "2026-07" for p in ongoing)
    assert all(p["ml"] is None for p in projects if p["status"] == "exited")
    findings = json.loads((a / "findings.json").read_text(encoding="utf-8"))
    assert findings["meta"]["headline"]["watchlist_size"] == 100
    assert "Did the model beat" in findings["assistant"][7]["question"] and "positives=" in findings["assistant"][7]["answer"]
    nums = json.loads((a / "numbers.json").read_text(encoding="utf-8"))
    assert "m1_HGB_B_recall_at_100" in nums and "m2_HGB_mae" in nums
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/models/test_pipeline.py -q` → FAIL (`models are not wired yet`).

- [ ] **Step 3: Write `findings/models/pipeline.py`**

```python
"""Runs M1-M4 once, assembles models.json, the per-project ml blocks, extra flags and the model card."""
import os
from datetime import datetime, timezone

import sklearn

from findings.features import pair_frame
from findings.models import m1_slip, m2_progress, m3_drivers, m4_anomaly, model_card
from findings.panel import latest, pairs_present, series

CONTRACT_VERSION = "1.0.0"


def run(panel, flags, sectors):
    pair_list = pairs_present(panel)
    frames = {pid: pair_frame(panel, a, b, flags) for pid, a, b in pair_list}
    test_pair = pair_list[-1][0]
    m1, p1, pairs_meta = m1_slip.run(panel, flags, frames, pair_list, test_pair=test_pair)
    m2, p2 = m2_progress.run(panel, flags, frames, pair_list, test_pair=test_pair)
    m3, p3 = m3_drivers.run(panel, flags)
    m4, p4, extra = m4_anomaly.run(panel)
    last = latest(panel)
    ml = {}
    for code, rs in series(panel).items():
        if rs[-1]["snapshot"] != last:
            continue
        a, b, c, d = p1.get(code, {}), p2.get(code, {}), p3.get(code, {}), p4.get(code, {})
        ml[code] = {"slip_prob": a.get("slip_prob"), "slip_rank": a.get("slip_rank"), "slip_top_factors": a.get("slip_top_factors", []),
                    "progress_next_pred": b.get("progress_next_pred"), "expected_completion": b.get("expected_completion"),
                    "expected_delay_months": b.get("expected_delay_months"),
                    "peer_expected_cost_overrun_pct": c.get("peer_expected_cost_overrun_pct"), "cost_overrun_residual_pct": c.get("cost_overrun_residual_pct"),
                    "peer_expected_time_overrun_months": c.get("peer_expected_time_overrun_months"), "time_overrun_residual_months": c.get("time_overrun_residual_months"),
                    "anomaly_score": d.get("anomaly_score"), "anomaly_flag": bool(d.get("anomaly_flag", False)), "scored_at_snapshot": last}
    generated = os.environ.get("AGRIM_GENERATED_AT") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    models = {"meta": {"contract_version": CONTRACT_VERSION, "generated_at": generated,
                       "sklearn_version": sklearn.__version__, "random_state": 0, "omp_threads": int(os.environ.get("OMP_NUM_THREADS", "1")),
                       "pairs": pairs_meta, "test_pair": test_pair, "train_pairs": [pid for pid, _, _ in pair_list[:-1]]},
              "m1_slip": m1, "m2_progress": m2, "m3_drivers": m3, "m4_anomaly": m4}
    return models, ml, extra, model_card.build(models, panel)
```

- [ ] **Step 4: Write `findings/models/model_card.py`**

```python
"""Outcome (i): the model card, generated from models.json so it can never drift from the numbers."""
from collections import Counter

from findings.features import FEATURES_A, FEATURES_B
from findings.panel import snapshots_present


def _pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}%"


def build(models, panel):
    m, counts = models["meta"], Counter(panel["snapshot"])
    test = m["test_pair"]
    res = {r["model_id"]: r for r in models["m1_slip"]["results"] if r["test_pair"] == test}
    sections = [
        {"title": "Data", "lines": [f"{len(snapshots_present(panel))} public MoSPI Flash Reports: " + ", ".join(f"{s} ({counts[s]} rows)" for s in snapshots_present(panel)),
                                    "Nine public fields per project; the Common Upload Form itself is behind role-based login and is not seen by any model."]},
        {"title": "Universe and censoring", "lines": [f"Pair {p['id']} ({p['from']} → {p['to']}, gap {p['gap_months']} months): n={p['n']}, positives={p['positives']}, exits excluded from labels={p['censored_exits']}" for p in m["pairs"]]},
        {"title": "Targets", "lines": ["M1: a revised completion date is filed in the next report (a reporting event, not a physical outcome).",
                                       "M2: next-month reported physical progress (points).",
                                       "M3: cross-sectional cost and time overrun on the latest report (drivers and peer benchmark, not a forecast).",
                                       "Cost escalation is not a forecast target: too few revision events in the window to train anything defensible."]},
        {"title": "Feature sets", "lines": ["A (public table fields): " + ", ".join(FEATURES_A), "B = A + audit-derived and history features: " + ", ".join(f for f in FEATURES_B if f not in FEATURES_A)]},
        {"title": "Validation", "lines": [f"Out-of-time: trained on {', '.join(m['train_pairs'])}, tested on {test}. No random splits. Label-shuffle control included.",
                                          f"random_state={m['random_state']}, OMP_NUM_THREADS={m['omp_threads']}, scikit-learn {m['sklearn_version']}."]},
        {"title": "M1 results on the held-out pair", "lines": [f"{mid}: PR-AUC {r['pr_auc']:.3f}, precision@100 {_pct(r['precision_at_100'])}, recall@100 {_pct(r['recall_at_100'])}, lift@100 {r['lift_at_100'] if r['lift_at_100'] is None else round(r['lift_at_100'], 2)} (n={r['n']}, positives={r['positives']}, base rate {_pct(r['base_rate'])})" for mid, r in res.items()]},
        {"title": "M2 results", "lines": [f"{r['model_id']}: MAE {r['mae']:.2f} points (median {r['median_ae']:.2f}, n={r['n']})" for r in models["m2_progress"]["results"]] + [f"Winner: {models['m2_progress']['winner']}"]},
        {"title": "M3 results (5-fold CV)", "lines": [f"{r['target']} / {r['model_id']}: R² {r['cv_r2']:.3f}, MAE {r['cv_mae']:.2f}" for r in models["m3_drivers"]["results"]]},
        {"title": "Known limitations", "lines": ["Labels are reporting events filtered through each agency's incentive to delay bad news.",
                                                 "The panel is survivor-selected: projects that leave are excluded from labels and counted above.",
                                                 "Nine fields; no milestones, contracts or site data. With PAIMANA access the same pipeline would consume the full CUF."]},
    ]
    return {"generated_at": m["generated_at"], "sections": sections}
```

- [ ] **Step 5: Wire the hook in `findings/run.py`**

Edit `findings/run.py`: replace the line `run_models = None  # Task 14 assigns findings.models.pipeline.run here` with:
```python
from findings.models import pipeline  # noqa: E402  (after OMP_NUM_THREADS is set)
run_models = pipeline.run
```

- [ ] **Step 6: Run the test, then the real data**

Run: `pytest tests/models/test_pipeline.py -q` → 1 passed (two full synthetic runs, a few minutes).

Run:
```powershell
python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json
python tools/render_pages.py
python tools/validate.py
```
Expected: `wrote web\public\data: ...`; validator `ok   models: valid`, `ok   model_card: valid`, `ok   deck/numbers.json all traceable`, `RESULT: PASS`.

Read `web/public/data/model_card.json` section "M1 results on the held-out pair" and post the four lines in the group chat. If `positives` on P4 is under 30, the model beat in the pitch leads with M2 and M3 (BUILD.md §12 row 13); write that decision in the PR.

- [ ] **Step 7: Commit the outputs**

```powershell
git switch -c task/14-pipeline
git add -A
git commit -m "task 14: models wired into the pipeline; model card; real-data models.json committed"
git push -u origin task/14-pipeline
gh pr create --title "Task 14: full pipeline with models" --body "<paste validate output and the four M1 result lines>"
```

---

### Task 15: Web app scaffold, data layer with contract validation, layout, Overview screen

**Files:**
- Create (all under `web/`): the Vite scaffold, `vite.config.ts`, `scripts/sync-contracts.mjs`, `scripts/check-dist.mjs`, `src/index.css`, `src/main.tsx`, `src/App.tsx`, `src/data/load.ts`, `src/data/store.tsx`, `src/lib/format.ts`, `src/lib/echart.ts`, `src/components/Layout.tsx`, `src/components/Badge.tsx`, `src/components/KPI.tsx`, `src/components/DataTable.tsx`, `src/screens/Placeholder.tsx`, `src/screens/Overview.tsx`
- Test: `npm run build` (type-check + bundle + `check-dist`) and `python tools/validate.py` (literal grep).

**Interfaces:**
- Consumes: `web/public/data/*.json` (Tasks 9 and 14), `contracts/*.schema.json`.
- Produces: `useBundle()` from `src/data/store.tsx` returning `{ bundle, error, sector, setSector }` where `bundle: Bundle | null` and `Bundle = { projects, findings, models, briefs, modelCard, byCode: Map<string, Project> }`; `DataTable<T>` component; `useEChart(option, deps)` hook; `format.ts` helpers `crore`, `pct`, `num`, `monthLabel`, `sevClass`, `bandClass`; the route table in `App.tsx` (later tasks swap `Placeholder` for real screens, one line each).
- Number rule for all TS: write pixel sizes as strings with `px` (`"520px"`), keep other numeric literals under 100 except `100`/`1000`; every displayed number comes from the JSON.

- [ ] **Step 1: Scaffold and install**

Run (PowerShell, from `C:\dev\agrim`):
```powershell
npm create vite@latest web -- --template react-ts
Set-Location web
npm install
npm install react-router-dom@6 echarts@6 @tanstack/react-table@8 @tanstack/react-virtual@3 ajv@8 lucide-react @fontsource/ibm-plex-sans @fontsource/ibm-plex-mono tailwindcss @tailwindcss/vite
npm install -D json-schema-to-typescript
```
Expected: `web/node_modules` exists; no peer-dependency errors. Delete the scaffold's `src/App.css` and `src/assets/react.svg`.

- [ ] **Step 2: Config, scripts, styles**

`web/vite.config.ts`:
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: { outDir: "dist", emptyOutDir: true },
});
```

In `web/tsconfig.app.json`, inside `compilerOptions`, add `"resolveJsonModule": true` (keep everything else the scaffold wrote).

`web/scripts/sync-contracts.mjs`:
```js
import { copyFileSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";
const src = join(process.cwd(), "..", "contracts");
const dst = join(process.cwd(), "src", "contracts");
mkdirSync(dst, { recursive: true });
for (const f of readdirSync(src).filter((f) => f.endsWith(".schema.json"))) copyFileSync(join(src, f), join(dst, f));
console.log("contracts synced");
```

`web/scripts/check-dist.mjs`:
```js
import { existsSync, readFileSync } from "node:fs";
const html = "dist/index.html";
if (!existsSync(html)) { console.error("dist/index.html missing"); process.exit(1); }
const t = readFileSync(html, "utf8");
if (!t.includes("/assets/")) { console.error("dist/index.html does not reference /assets/"); process.exit(1); }
console.log("dist ok");
```

Replace the `scripts` block of `web/package.json` with:
```json
"scripts": {
  "sync": "node scripts/sync-contracts.mjs",
  "types": "json2ts -i src/contracts/projects.schema.json -o src/types/projects.d.ts && json2ts -i src/contracts/findings.schema.json -o src/types/findings.d.ts && json2ts -i src/contracts/models.schema.json -o src/types/models.d.ts && json2ts -i src/contracts/briefs.schema.json -o src/types/briefs.d.ts && json2ts -i src/contracts/model_card.schema.json -o src/types/model_card.d.ts",
  "predev": "npm run sync && npm run types",
  "prebuild": "npm run sync && npm run types",
  "dev": "vite",
  "build": "tsc -b && vite build && node scripts/check-dist.mjs",
  "preview": "vite preview"
}
```

`web/src/index.css`:
```css
@import "@fontsource/ibm-plex-sans/400.css";
@import "@fontsource/ibm-plex-sans/500.css";
@import "@fontsource/ibm-plex-sans/600.css";
@import "@fontsource/ibm-plex-mono/400.css";
@import "@fontsource/ibm-plex-mono/500.css";
@import "tailwindcss";

@theme {
  --color-ground: #F4F6F8;
  --color-surface: #FFFFFF;
  --color-ink: #0E1A2B;
  --color-muted: #4B5A6B;
  --color-line: #D5DCE4;
  --color-accent: #1F5FA8;
  --color-critical: #B42318;
  --color-high: #C2410C;
  --color-medium: #B7791F;
  --color-ok: #1E7B4F;
  --color-model: #5B4B9A;
  --font-sans: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}

html { color-scheme: light; }
body { margin: 0; background: var(--color-ground); color: var(--color-ink); font-family: var(--font-sans); font-size: 15px; line-height: 1.5; }
.num { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
a { color: var(--color-accent); }
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
```

- [ ] **Step 3: Generate the types and check their names**

Run: `npm run sync && npm run types`
Expected: five files under `web/src/types/`. Open `src/types/projects.d.ts` and confirm it exports `Projects` and `Project` (json2ts names the array by the schema title and the item by the `$defs` key). Do the same for `Findings`, `Models`, `Briefs`, `ModelCard`. If a name differs, use the generated name in the imports below; do not edit the generated files.

- [ ] **Step 4: Data layer**

`web/src/data/load.ts`:
```ts
import Ajv2020 from "ajv/dist/2020";
import projectsSchema from "../contracts/projects.schema.json";
import findingsSchema from "../contracts/findings.schema.json";
import modelsSchema from "../contracts/models.schema.json";
import briefsSchema from "../contracts/briefs.schema.json";
import modelCardSchema from "../contracts/model_card.schema.json";
import type { Project, Projects } from "../types/projects";
import type { Findings } from "../types/findings";
import type { Models } from "../types/models";
import type { Briefs } from "../types/briefs";
import type { ModelCard } from "../types/model_card";

export interface Bundle {
  projects: Projects;
  findings: Findings;
  models: Models | null;
  briefs: Briefs | null;
  modelCard: ModelCard | null;
  byCode: Map<string, Project>;
}

const ajv = new Ajv2020({ allErrors: false, strict: false });

async function fetchJson(path: string): Promise<unknown | null> {
  const r = await fetch(path);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}

function validate<T>(name: string, schema: object, data: unknown): T {
  const check = ajv.compile(schema);
  if (!check(data)) {
    const e = check.errors?.[0];
    throw new Error(`${name} violates the contract at "${e?.instancePath ?? ""}": ${e?.message ?? "unknown"}`);
  }
  return data as T;
}

export async function loadBundle(): Promise<Bundle> {
  const [p, f, m, b, c] = await Promise.all([
    fetchJson("data/projects.json"), fetchJson("data/findings.json"), fetchJson("data/models.json"),
    fetchJson("data/briefs.json"), fetchJson("data/model_card.json"),
  ]);
  if (p == null || f == null) throw new Error("projects.json and findings.json are required (run findings/run.py)");
  const projects = validate<Projects>("projects.json", projectsSchema, p);
  const findings = validate<Findings>("findings.json", findingsSchema, f);
  const models = m == null ? null : validate<Models>("models.json", modelsSchema, m);
  const briefs = b == null ? null : validate<Briefs>("briefs.json", briefsSchema, b);
  const modelCard = c == null ? null : validate<ModelCard>("model_card.json", modelCardSchema, c);
  return { projects, findings, models, briefs, modelCard, byCode: new Map(projects.map((x) => [x.project_code, x])) };
}
```

`web/src/data/store.tsx`:
```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { loadBundle, type Bundle } from "./load";

interface Store { bundle: Bundle | null; error: string | null; sector: string | null; setSector: (s: string | null) => void }
const Ctx = createContext<Store>({ bundle: null, error: null, sector: null, setSector: () => {} });

export function StoreProvider({ children }: { children: ReactNode }) {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sector, setSector] = useState<string | null>(null);
  useEffect(() => { loadBundle().then(setBundle).catch((e: Error) => setError(e.message)); }, []);
  return <Ctx.Provider value={{ bundle, error, sector, setSector }}>{children}</Ctx.Provider>;
}

export const useBundle = () => useContext(Ctx);
```

`web/src/lib/format.ts`:
```ts
const inr2 = new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const inr0 = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
export const crore = (v: number | null | undefined) => (v == null ? "—" : `₹ ${inr2.format(v)} cr`);
export const num = (v: number | null | undefined, d = 0) => (v == null ? "—" : d === 0 ? inr0.format(v) : v.toFixed(d));
export const pct = (v: number | null | undefined, d = 1) => (v == null ? "—" : `${v.toFixed(d)}%`);
export const share = (v: number | null | undefined) => (v == null ? "—" : `${(v * 100).toFixed(0)}%`);
export const monthLabel = (ym: string | null | undefined) =>
  ym ? new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1, 1).toLocaleString("en-IN", { month: "short", year: "numeric" }) : "—";
export const sevClass: Record<string, string> = {
  critical: "bg-critical text-white", high: "bg-high text-white", medium: "bg-medium text-white", low: "bg-line text-ink", info: "bg-line text-muted",
};
export const bandClass: Record<string, string> = { red: "bg-critical text-white", amber: "bg-medium text-white", green: "bg-ok text-white" };
```

`web/src/lib/echart.ts`:
```ts
import * as echarts from "echarts";
import { useEffect, useRef } from "react";

export function useEChart(option: echarts.EChartsOption, deps: unknown[]) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    chart.setOption(option, true);
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => { window.removeEventListener("resize", onResize); chart.dispose(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return ref;
}
```

- [ ] **Step 5: Components**

`web/src/components/Badge.tsx`:
```tsx
export function Badge({ text, className }: { text: string; className: string }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${className}`}>{text}</span>;
}
```

`web/src/components/KPI.tsx`:
```tsx
export function KPI({ label, value, hint, model = false }: { label: string; value: string; hint?: string; model?: boolean }) {
  return (
    <div className={`rounded border bg-surface px-4 py-3 ${model ? "border-model" : "border-line"}`}>
      <div className="text-xs uppercase tracking-wide text-muted">{label}{model ? " · model" : ""}</div>
      <div className={`num text-2xl font-medium ${model ? "text-model" : ""}`}>{value}</div>
      {hint && <div className="text-xs text-muted">{hint}</div>}
    </div>
  );
}
```

`web/src/components/DataTable.tsx`:
```tsx
import { flexRender, getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef, useState } from "react";

export function DataTable<T>({ columns, rows, onRowClick, height = "520px" }:
  { columns: ColumnDef<T, unknown>[]; rows: T[]; onRowClick?: (row: T) => void; height?: string }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({ data: rows, columns, state: { sorting }, onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(), getSortedRowModel: getSortedRowModel() });
  const parentRef = useRef<HTMLDivElement>(null);
  const trows = table.getRowModel().rows;
  const v = useVirtualizer({ count: trows.length, getScrollElement: () => parentRef.current, estimateSize: () => 36, overscan: 12 });
  const items = v.getVirtualItems();
  const before = items.length ? items[0].start : 0;
  const after = items.length ? v.getTotalSize() - items[items.length - 1].end : 0;
  return (
    <div ref={parentRef} className="overflow-auto rounded border border-line bg-surface" style={{ height }}>
      <table className="w-full border-collapse text-sm">
        <thead className="sticky top-0 z-10 bg-surface">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th key={h.id} onClick={h.column.getToggleSortingHandler()}
                  className="cursor-pointer select-none border-b border-line px-3 py-2 text-left text-xs uppercase tracking-wide text-muted">
                  {flexRender(h.column.columnDef.header, h.getContext())}
                  {{ asc: " ↑", desc: " ↓" }[h.column.getIsSorted() as string] ?? ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {before > 0 && <tr><td colSpan={columns.length} style={{ height: `${before}px` }} /></tr>}
          {items.map((vi) => {
            const row = trows[vi.index];
            return (
              <tr key={row.id} onClick={() => onRowClick?.(row.original)}
                className={`border-b border-line ${onRowClick ? "cursor-pointer hover:bg-ground" : ""}`} style={{ height: "36px" }}>
                {row.getVisibleCells().map((c) => <td key={c.id} className="px-3 py-1 align-middle">{flexRender(c.column.columnDef.cell, c.getContext())}</td>)}
              </tr>
            );
          })}
          {after > 0 && <tr><td colSpan={columns.length} style={{ height: `${after}px` }} /></tr>}
        </tbody>
      </table>
      {rows.length === 0 && <div className="p-6 text-sm text-muted">Nothing to show for this filter.</div>}
    </div>
  );
}
```

`web/src/components/Layout.tsx`:
```tsx
import { NavLink, Outlet } from "react-router-dom";
import { useBundle } from "../data/store";

const GROUPS: { title: string; items: [string, string][] }[] = [
  { title: "Audit", items: [["/", "Overview"], ["/ledger", "Contradiction Ledger"], ["/exits", "Exit Ledger"], ["/fields", "Field Audit"]] },
  { title: "Outlook", items: [["/warning", "Early Warning"], ["/predict", "Predictions"], ["/drivers", "Drivers & Benchmark"]] },
  { title: "About", items: [["/assistant", "Assistant"], ["/model-card", "Model Card"]] },
];

export function Layout() {
  const { bundle, error, sector, setSector } = useBundle();
  const cov = bundle?.findings.meta.coverage ?? [];
  const rows = cov.reduce((a, c) => a + c.rows_parsed, 0);
  const pcts = cov.filter((c) => c.pct != null).map((c) => c.pct as number);
  const avg = pcts.length ? pcts.reduce((a, b) => a + b, 0) / pcts.length : null;
  const sectors = bundle?.findings.by_sector.map((g) => g.key) ?? [];
  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 border-r border-line bg-surface px-3 py-4">
        <div className="mb-4 px-2 font-semibold tracking-tight">AGRIM</div>
        {GROUPS.map((g) => (
          <div key={g.title} className="mb-4">
            <div className="px-2 text-xs uppercase tracking-wide text-muted">{g.title}</div>
            {g.items.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === "/"}
                className={({ isActive }) => `block rounded px-2 py-1 text-sm ${isActive ? "bg-ground font-medium" : "text-ink hover:bg-ground"}`}>{label}</NavLink>
            ))}
          </div>
        ))}
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center gap-3 border-b border-line bg-surface px-4">
          <select className="rounded border border-line bg-surface px-2 py-1 text-sm" value={sector ?? ""} onChange={(e) => setSector(e.target.value || null)}>
            <option value="">IPMD · national view</option>
            {sectors.map((s) => <option key={s} value={s}>Ministry officer · {s}</option>)}
          </select>
          {bundle && (
            <span className="rounded border border-line px-2 py-1 text-xs text-muted">
              {cov.length} reports · <span className="num">{rows}</span> rows{avg != null ? <> · <span className="num">{avg.toFixed(1)}%</span> parsed</> : null}
            </span>
          )}
          <div className="flex-1" />
          <div id="header-actions" className="flex items-center gap-2" />
        </header>
        <main className="mx-auto w-full max-w-[1440px] flex-1 p-4">
          {error && <div className="rounded border border-critical bg-surface p-4 text-critical">Data failed to load: {error}</div>}
          {!bundle && !error && <div className="p-6 text-muted">Loading the five reports…</div>}
          {bundle && <Outlet />}
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Screens, routes, entry**

`web/src/screens/Placeholder.tsx`:
```tsx
export function Placeholder({ name }: { name: string }) {
  return <div className="rounded border border-line bg-surface p-6 text-muted">{name} arrives in a later task.</div>;
}
```

`web/src/screens/Overview.tsx`:
```tsx
import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { KPI } from "../components/KPI";
import { useBundle } from "../data/store";
import { bandClass, crore, num, pct, share } from "../lib/format";
import type { Project } from "../types/projects";

export function Overview() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const h = bundle!.findings.meta.headline;
  const latest = bundle!.findings.meta.snapshots[bundle!.findings.meta.snapshots.length - 1];
  const rows = useMemo(() => bundle!.projects
    .filter((p) => p.status === "ongoing" && (!sector || p.sector === sector))
    .sort((a, b) => b.risk.score - a.risk.score || (b.ml?.slip_prob ?? 0) - (a.ml?.slip_prob ?? 0))
    .slice(0, 20), [bundle, sector]);
  const columns: ColumnDef<Project, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "State", accessorKey: "state" },
    { header: "Progress", accessorFn: (p) => p.snapshots[p.snapshots.length - 1].physical_progress_pct, cell: (c) => <span className="num">{pct(c.getValue() as number | null)}</span> },
    { header: "Rule risk", accessorFn: (p) => p.risk.score, cell: (c) => <Badge text={`${c.row.original.risk.band} · ${num(c.getValue() as number)}`} className={bandClass[c.row.original.risk.band]} /> },
    { header: "Slip prob. (model)", accessorFn: (p) => p.ml?.slip_prob ?? null, cell: (c) => <span className="num text-model">{share(c.getValue() as number | null)}</span> },
  ];
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
        <KPI label={`Projects · ${latest}`} value={num(h.projects_latest)} />
        <KPI label="Revised cost" value={crore(h.cost_revised_total_cr)} />
        <KPI label="Recorded overrun" value={crore(h.overrun_total_cr)} hint="revised minus original" />
        <KPI label="Contradictions" value={num(h.contradictions_total)} hint="arithmetic impossibilities" />
        <KPI label="Left the panel" value={num(h.exits_total)} />
        <KPI label="Unreachable dates" value={num(h.unreachable_total)} hint="at own reported pace" />
        <KPI label="Watchlist" value={num(h.watchlist_size)} model />
      </div>
      <div id="overview-map" />
      <h2 className="text-lg font-semibold">Top 20 by rule-based risk{sector ? ` · ${sector}` : ""}</h2>
      <DataTable columns={columns} rows={rows} onRowClick={(p) => nav(`/project/${p.project_code}`)} height="720px" />
    </div>
  );
}
```

`web/src/App.tsx`:
```tsx
import { HashRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { StoreProvider } from "./data/store";
import { Overview } from "./screens/Overview";
import { Placeholder } from "./screens/Placeholder";

export default function App() {
  return (
    <StoreProvider>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Overview />} />
            <Route path="/ledger" element={<Placeholder name="Contradiction Ledger" />} />
            <Route path="/project/:code" element={<Placeholder name="Project" />} />
            <Route path="/exits" element={<Placeholder name="Exit Ledger" />} />
            <Route path="/warning" element={<Placeholder name="Early Warning" />} />
            <Route path="/predict" element={<Placeholder name="Predictions" />} />
            <Route path="/drivers" element={<Placeholder name="Drivers & Benchmark" />} />
            <Route path="/fields" element={<Placeholder name="Field Audit" />} />
            <Route path="/assistant" element={<Placeholder name="Assistant" />} />
            <Route path="/model-card" element={<Placeholder name="Model Card" />} />
          </Route>
        </Routes>
      </HashRouter>
    </StoreProvider>
  );
}
```

`web/src/main.tsx`:
```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
```

In `web/index.html`, set `<title>AGRIM</title>` and leave the rest of the scaffold.

- [ ] **Step 7: Build, run, look**

Run: `npm run build` → Expected: `tsc` clean, Vite bundle summary, `dist ok`. If `tsc` complains about the generated type names, fix the imports (Step 3), not the generated files.

Run: `npm run dev` and open `http://localhost:5173/#/`. Expected: KPI strip with real numbers, the top-20 table, sector select working. Stop the dev server.

Run (from repo root): `python tools/validate.py` → `ok   no hardcoded numbers in N files`, `RESULT: PASS`. If it flags a literal, rewrite it as a `px` string or read it from data.

- [ ] **Step 8: Commit**

```powershell
git switch -c task/15-web-scaffold
git add -A
git commit -m "task 15: web scaffold, contract-validated data layer, layout, overview"
git push -u origin task/15-web-scaffold
gh pr create --title "Task 15: web scaffold + overview" --body "<paste build and validate output>"
```

---

### Task 16: Contradiction Ledger and Project screens

**Files:**
- Create: `web/src/screens/Ledger.tsx`, `web/src/screens/Project.tsx`, `web/src/components/Sparkline.tsx`, `web/src/components/SourcePage.tsx`
- Modify: `web/src/App.tsx` (two route lines)

**Interfaces:**
- Consumes: `useBundle()`, `DataTable`, `useEChart`, `findings.contradictions.rows`, `projects[].snapshots|flags|risk|ml`, page images at `pages/<snapshot>/p<page>.png`.
- Produces: route `#/ledger?type=<TYPE>` and `#/project/:code`; `Sparkline({ labels, values, forecast?, color })`; `SourcePage({ snapshot, page })` modal.

- [ ] **Step 1: Sparkline and SourcePage components**

`web/src/components/Sparkline.tsx`:
```tsx
import { useEChart } from "../lib/echart";

export function Sparkline({ labels, values, forecast, color, unit }:
  { labels: string[]; values: (number | null)[]; forecast?: number | null; color: string; unit: string }) {
  const xs = forecast != null ? [...labels, "next (model)"] : labels;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 28 },
    xAxis: { type: "category", data: xs, axisLabel: { fontSize: 10 } },
    yAxis: { type: "value", axisLabel: { fontSize: 10 }, name: unit, nameTextStyle: { fontSize: 10 } },
    tooltip: { trigger: "axis" },
    series: [
      { type: "line", data: values, color, showSymbol: true, symbolSize: 6, areaStyle: { opacity: 0.08 } },
      ...(forecast != null ? [{ type: "line" as const, data: [...values.map(() => null), forecast].map((v, i) => (i === values.length - 1 ? values[i] : v)),
        color: "#5B4B9A", lineStyle: { type: "dashed" as const }, showSymbol: true, symbolSize: 6 }] : []),
    ],
  }, [labels.join(), values.join(), forecast, color]);
  return <div ref={ref} style={{ height: "180px" }} />;
}
```

`web/src/components/SourcePage.tsx`:
```tsx
import { useState } from "react";

export function SourcePage({ snapshot, page }: { snapshot: string; page: number }) {
  const [open, setOpen] = useState(false);
  const src = `pages/${snapshot}/p${page}.png`;
  return (
    <>
      <button className="rounded border border-accent px-2 py-1 text-xs text-accent hover:bg-ground" onClick={() => setOpen(true)}>
        Source page · {snapshot} p.{page}
      </button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-6" onClick={() => setOpen(false)}>
          <div className="max-h-full max-w-5xl overflow-auto rounded bg-surface p-2" onClick={(e) => e.stopPropagation()}>
            <div className="mb-2 flex items-center justify-between text-sm"><span>MoSPI Flash Report {snapshot}, page {page} (rendered from the PDF)</span>
              <button className="text-accent" onClick={() => setOpen(false)}>Close</button></div>
            <img src={src} alt={`Flash Report ${snapshot} page ${page}`} className="max-w-full"
              onError={(e) => { (e.currentTarget as HTMLImageElement).alt = "Page image not rendered — run python tools/render_pages.py"; }} />
          </div>
        </div>
      )}
    </>
  );
}
```

- [ ] **Step 2: Ledger screen**

`web/src/screens/Ledger.tsx`:
```tsx
import type { ColumnDef } from "@tanstack/react-table";
import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { crore, sevClass } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["contradictions"]["rows"][number];
const ORDER = ["EXP_DECREASE", "PROG_DECREASE", "EXP_GT_REVISED_COST", "ZERO_PROG_NONZERO_EXP", "PROG_GT_100", "DOC_BEFORE_APPROVAL", "STAT_ANOMALY"];
const LABEL: Record<string, string> = { EXP_DECREASE: "Cumulative expenditure fell", PROG_DECREASE: "Progress fell", EXP_GT_REVISED_COST: "Spent more than revised cost",
  ZERO_PROG_NONZERO_EXP: "0% progress, money spent", PROG_GT_100: "Progress above 100%", DOC_BEFORE_APPROVAL: "Completion before approval", STAT_ANOMALY: "Statistical outlier (model)" };

const fmt = (t: string, v: number | string | null) => (v == null ? "—" : typeof v === "number" ? (t === "PROG_DECREASE" || t === "PROG_GT_100" || t === "ZERO_PROG_NONZERO_EXP" ? `${v}%` : crore(v)) : v);

export function Ledger() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const type = params.get("type") ?? "";
  const counts = new Map(bundle!.findings.contradictions.by_type.map((t) => [t.type, t.count]));
  const rows = useMemo(() => bundle!.findings.contradictions.rows.filter((r) => (!type || r.type === type) &&
    (!sector || bundle!.byCode.get(r.project_code)?.sector === sector)), [bundle, type, sector]);
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Type", accessorKey: "type", cell: (c) => LABEL[c.getValue() as string] ?? (c.getValue() as string) },
    { header: "Months", accessorFn: (r) => `${r.from_snapshot ?? ""} → ${r.to_snapshot}`, cell: (c) => <span className="num">{c.getValue() as string}</span> },
    { header: "Before", accessorKey: "before", cell: (c) => <span className="num">{fmt(c.row.original.type, c.getValue() as number | string | null)}</span> },
    { header: "After", accessorKey: "after", cell: (c) => <span className="num">{fmt(c.row.original.type, c.getValue() as number | string | null)}</span> },
    { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> },
    { header: "Page", accessorFn: (r) => r.sources[r.sources.length - 1]?.page ?? null, cell: (c) => <span className="num">{String(c.getValue() ?? "—")}</span> },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Contradiction Ledger</h1>
      <p className="max-w-3xl text-sm text-muted">Each row is a statement in the Ministry's own report that cannot be true alongside another statement in the same or the previous report. Every row carries the page it was read from.</p>
      <div className="flex flex-wrap gap-2">
        <button onClick={() => setParams({})} className={`rounded border px-2 py-1 text-xs ${!type ? "border-accent bg-ground" : "border-line"}`}>All · {bundle!.findings.contradictions.rows.length}</button>
        {ORDER.filter((t) => counts.has(t)).map((t) => (
          <button key={t} onClick={() => setParams({ type: t })} className={`rounded border px-2 py-1 text-xs ${type === t ? "border-accent bg-ground" : "border-line"}`}>{LABEL[t]} · {counts.get(t)}</button>
        ))}
      </div>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="680px" />
    </div>
  );
}
```

- [ ] **Step 3: Project screen**

`web/src/screens/Project.tsx`:
```tsx
import { useParams } from "react-router-dom";
import { Badge } from "../components/Badge";
import { SourcePage } from "../components/SourcePage";
import { Sparkline } from "../components/Sparkline";
import { useBundle } from "../data/store";
import { bandClass, crore, monthLabel, num, pct, sevClass, share } from "../lib/format";

export function Project() {
  const { code } = useParams();
  const { bundle } = useBundle();
  const p = code ? bundle!.byCode.get(code) : undefined;
  if (!p) return <div className="text-muted">No project with code {code}.</div>;
  const last = p.snapshots[p.snapshots.length - 1];
  const prev = p.snapshots.length > 1 ? p.snapshots[p.snapshots.length - 2] : null;
  const labels = p.snapshots.map((s) => s.snapshot);
  const brief = bundle!.briefs?.find((b) => b.project_code === p.project_code) ?? null;
  const ml = p.ml;
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="num text-sm text-muted">{p.project_code}{p.agency_raw ? ` · ${p.agency_raw}` : ""}{p.state ? ` · ${p.state}` : ""}{p.sector ? ` · ${p.sector}` : ""}</div>
          <h1 className="text-xl font-semibold">{p.project_name}</h1>
          <div className="text-sm text-muted">Seen {p.first_seen} → {p.last_seen} · {p.status === "exited" ? "left the monitored panel" : "ongoing"} · stated completion {monthLabel(last.doc_revised ?? last.doc_original)}{last.doc_revised ? ` (revised from ${monthLabel(last.doc_original)})` : ""}</div>
        </div>
        <div className="flex items-center gap-2">
          <Badge text={`${p.risk.band} · rule score ${num(p.risk.score)}`} className={bandClass[p.risk.band]} />
          <SourcePage snapshot={last.snapshot} page={last.page} />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Physical progress</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.physical_progress_pct)} forecast={ml?.progress_next_pred ?? null} color="#1F5FA8" unit="%" />
        </div>
        <div className="rounded border border-line bg-surface p-3">
          <div className="text-xs uppercase tracking-wide text-muted">Cumulative expenditure (₹ cr)</div>
          <Sparkline labels={labels} values={p.snapshots.map((s) => s.expenditure_cum_cr)} color="#1E7B4F" unit="₹ cr" />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3">
          <div className="mb-2 text-xs uppercase tracking-wide text-muted">Flags · {p.flags.length}</div>
          {p.flags.length === 0 && <div className="text-sm text-muted">No flags. The record is internally consistent across the reports we parsed.</div>}
          <ul className="space-y-2">
            {p.flags.map((f, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <Badge text={f.severity} className={sevClass[f.severity]} />
                <span>{f.detail} {f.sources.map((s) => <SourcePage key={`${s.snapshot}-${s.page}`} snapshot={s.snapshot} page={s.page} />)}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className={`rounded border bg-surface p-3 ${ml ? "border-model" : "border-line"}`}>
          <div className="mb-2 text-xs uppercase tracking-wide text-model">Outlook · model</div>
          {!ml && <div className="text-sm text-muted">No model score for this project (exited, or models not run).</div>}
          {ml && (
            <div className="space-y-2 text-sm">
              <div>Chance a revised completion date is filed next report: <span className="num font-medium text-model">{share(ml.slip_prob)}</span>{ml.slip_rank != null && <span className="text-muted"> · rank {ml.slip_rank}</span>}</div>
              <ul className="space-y-1">
                {ml.slip_top_factors.map((f) => (
                  <li key={f.feature} className="flex items-center gap-2">
                    <span className="w-44 truncate text-muted" title={f.feature}>{f.feature}</span>
                    <span className="h-2 rounded bg-model" style={{ width: `${Math.min(96, Math.abs(f.contribution) * 60)}px`, opacity: f.contribution >= 0 ? 1 : 0.4 }} />
                    <span className="num text-xs">{f.contribution >= 0 ? "+" : ""}{f.contribution.toFixed(2)} · {f.value == null ? "—" : typeof f.value === "number" ? f.value.toFixed(1) : f.value}</span>
                  </li>
                ))}
              </ul>
              <div>Expected completion at the winning method's pace: <span className="num">{monthLabel(ml.expected_completion)}</span>{ml.expected_delay_months != null && <span> · <span className={`num ${ml.expected_delay_months > 0 ? "text-critical" : "text-ok"}`}>{ml.expected_delay_months > 0 ? "+" : ""}{num(ml.expected_delay_months)} months</span> vs stated date</span>}</div>
              {ml.cost_overrun_residual_pct != null && <div>Cost overrun vs comparable projects: <span className={`num ${ml.cost_overrun_residual_pct > 0 ? "text-critical" : "text-ok"}`}>{ml.cost_overrun_residual_pct > 0 ? "+" : ""}{pct(ml.cost_overrun_residual_pct)}</span> (peers expected {pct(ml.peer_expected_cost_overrun_pct)})</div>}
              {ml.anomaly_flag && <div className="text-muted">Flagged as a statistical outlier by the anomaly model.</div>}
            </div>
          )}
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 text-xs uppercase tracking-wide text-muted">Assistant · this project</div>
          <details open><summary className="cursor-pointer">Why is {p.project_code} rated {p.risk.band}?</summary>
            <ul className="mt-1 list-disc pl-5">{p.risk.reasons.length ? p.risk.reasons.map((r, i) => <li key={i}>{r}</li>) : <li>No contributing flags.</li>}</ul></details>
          <details><summary className="cursor-pointer">What changed between {prev?.snapshot ?? "—"} and {last.snapshot}?</summary>
            {prev ? <ul className="mt-1 list-disc pl-5">
              <li>Progress {pct(prev.physical_progress_pct)} → {pct(last.physical_progress_pct)}</li>
              <li>Expenditure {crore(prev.expenditure_cum_cr)} → {crore(last.expenditure_cum_cr)}</li>
              <li>Revised cost {crore(prev.cost_revised_cr)} → {crore(last.cost_revised_cr)}</li>
              <li>Revised date {monthLabel(prev.doc_revised)} → {monthLabel(last.doc_revised)}</li>
            </ul> : <div className="text-muted">Only one report has this project.</div>}</details>
        </div>
        <div className="rounded border border-line bg-surface p-3 text-sm">
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-muted">Brief {brief && <Badge text={`LLM · ${brief.model} · ${brief.grounded ? "verified against ledger" : "template fallback"}`} className="bg-line text-muted" />}</div>
          {brief ? <p>{brief.brief}</p> : <p className="text-muted">No cached brief for this project.</p>}
        </div>
      </div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">As printed, by report</div>
        <table className="w-full text-sm"><thead><tr className="text-left text-xs uppercase text-muted"><th>Report</th><th>Page</th><th>Original DoC</th><th>Revised DoC</th><th>Original cost</th><th>Revised cost</th><th>Expenditure</th><th>Progress</th></tr></thead>
          <tbody>{p.snapshots.map((s) => <tr key={s.snapshot} className="border-t border-line"><td className="num">{s.snapshot}</td><td className="num">{s.page}</td><td>{monthLabel(s.doc_original)}</td><td>{monthLabel(s.doc_revised)}</td><td className="num">{crore(s.cost_original_cr)}</td><td className="num">{crore(s.cost_revised_cr)}</td><td className="num">{crore(s.expenditure_cum_cr)}</td><td className="num">{pct(s.physical_progress_pct)}</td></tr>)}</tbody></table>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Wire the routes**

In `web/src/App.tsx`, add `import { Ledger } from "./screens/Ledger";` and `import { Project } from "./screens/Project";`, then replace the two placeholder routes with `<Route path="/ledger" element={<Ledger />} />` and `<Route path="/project/:code" element={<Project />} />`.

- [ ] **Step 5: Build, check, commit**

Run: `npm run build` (in `web/`) then `python tools/validate.py` (root) → both green. Run `npm run dev`, open `#/ledger?type=EXP_DECREASE`, click the 705526 row (or the top row), open its source page image. Expected: the PDF page renders in the modal.

```powershell
git switch -c task/16-ledger-project
git add -A
git commit -m "task 16: contradiction ledger and project screens with source-page images and outlook card"
git push -u origin task/16-ledger-project
gh pr create --title "Task 16: ledger + project" --body "<paste outputs>"
```

---

### Task 17: Exits, Early Warning, Field Audit, Predictions, Drivers screens

**Files:**
- Create: `web/src/screens/Exits.tsx`, `web/src/screens/Warning.tsx`, `web/src/screens/Fields.tsx`, `web/src/screens/Predict.tsx`, `web/src/screens/Drivers.tsx`
- Modify: `web/src/App.tsx` (five route lines)

**Interfaces:**
- Consumes: `findings.exits|early_warning|field_audit|by_sector|by_state`, `models.m1_slip|m2_progress|m3_drivers`, `projects[].ml`.
- Produces: the five routes.

- [ ] **Step 1: Exits**

`web/src/screens/Exits.tsx`:
```tsx
import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { crore, num, pct } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["exits"]["rows"][number];
const PART: Record<string, string> = { LAST_SEEN_GE_95: "≥95% when last seen", LAST_SEEN_50_95: "50–95% when last seen", LAST_SEEN_LT_50: "<50% when last seen", UNKNOWN: "progress not printed" };

export function Exits() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const ex = bundle!.findings.exits;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 28 }, legend: { top: 0 }, tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: ex.pairs.map((p) => `${p.from} → ${p.to}`) }, yAxis: { type: "value", name: "projects" },
    series: [
      { name: "left the panel", type: "bar", data: ex.pairs.map((p) => p.exited), color: "#B42318" },
      { name: "entered", type: "bar", data: ex.pairs.map((p) => p.entered), color: "#1E7B4F" },
      { name: "commissioned (printed)", type: "bar", data: ex.pairs.map((p) => p.commissioned_printed ?? 0), color: "#4B5A6B" },
    ],
  }, [ex]);
  const parts = new Map<string, number>();
  ex.rows.forEach((r) => parts.set(r.partition, (parts.get(r.partition) ?? 0) + 1));
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Last seen", accessorKey: "last_seen", cell: (c) => <span className="num">{c.getValue() as string}</span> },
    { header: "Progress", accessorKey: "last_progress_pct", cell: (c) => <span className="num">{pct(c.getValue() as number | null)}</span> },
    { header: "Expenditure", accessorKey: "last_expenditure_cr", cell: (c) => <span className="num">{crore(c.getValue() as number | null)}</span> },
    { header: "Revised cost", accessorKey: "last_cost_revised_cr", cell: (c) => <span className="num">{crore(c.getValue() as number | null)}</span> },
    { header: "State when last seen", accessorKey: "partition", cell: (c) => PART[c.getValue() as string] },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Exit Ledger</h1>
      <p className="max-w-3xl text-sm text-muted">Projects present in one report and absent from the next. These are net changes in the published panel; the reason a project leaves (commissioned, re-scoped, transferred, dropped) is a status field behind login, so rows are labelled by their last observed state, never as cancelled.</p>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "260px" }} /></div>
      <div className="flex flex-wrap gap-2 text-sm">{[...parts.entries()].map(([k, v]) => <span key={k} className="rounded border border-line bg-surface px-2 py-1">{PART[k]} · <span className="num">{num(v)}</span></span>)}
        <span className="rounded border border-line bg-surface px-2 py-1">recorded overrun that left: <span className="num">{crore(ex.pairs.reduce((a, p) => a + p.exited_cost_revised_cr, 0))}</span> (revised cost of exited rows)</span></div>
      <DataTable columns={columns} rows={ex.rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="520px" />
    </div>
  );
}
```

- [ ] **Step 2: Early Warning**

`web/src/screens/Warning.tsx`:
```tsx
import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, sevClass } from "../lib/format";
import type { Findings } from "../types/findings";

type Row = Findings["early_warning"]["rows"][number];

export function Warning() {
  const { bundle, sector } = useBundle();
  const nav = useNavigate();
  const rows = bundle!.findings.early_warning.rows.filter((r) => !sector || bundle!.byCode.get(r.project_code)?.sector === sector);
  const edges = [1, 1.25, 1.5, 2, 3, 5, 10];
  const bins = edges.map((e, i) => rows.filter((r) => r.ratio != null && r.ratio >= e && (i === edges.length - 1 || (r.ratio as number) < edges[i + 1])).length);
  const stalled = rows.filter((r) => r.ratio == null).length;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 28 }, tooltip: {},
    xAxis: { type: "category", data: [...edges.map((e, i) => (i === edges.length - 1 ? `≥${e}×` : `${e}–${edges[i + 1]}×`)), "no progress"] },
    yAxis: { type: "value", name: "projects" },
    series: [{ type: "bar", data: [...bins, stalled], color: "#C2410C" }],
  }, [rows.length]);
  const columns: ColumnDef<Row, unknown>[] = [
    { header: "Project", accessorKey: "project_name", cell: (c) => <span><span className="num text-muted">{c.row.original.project_code}</span> {c.getValue() as string}</span> },
    { header: "Pace (pt/month)", accessorKey: "velocity_pct_per_month", cell: (c) => <span className="num">{c.getValue() == null ? "—" : (c.getValue() as number).toFixed(2)}</span> },
    { header: "Months needed", accessorKey: "months_needed", cell: (c) => <span className="num">{c.getValue() == null ? "∞" : num(c.getValue() as number)}</span> },
    { header: "Months left", accessorKey: "months_remaining", cell: (c) => <span className="num">{num(c.getValue() as number)}</span> },
    { header: "Ratio", accessorKey: "ratio", cell: (c) => <span className="num">{c.getValue() == null ? "—" : `${(c.getValue() as number).toFixed(1)}×`}</span> },
    { header: "Severity", accessorKey: "severity", cell: (c) => <Badge text={c.getValue() as string} className={sevClass[c.getValue() as string]} /> },
  ];
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Early Warning · unreachable completion dates</h1>
      <p className="max-w-3xl text-sm text-muted">No model. For each project, the progress rate it reports itself is compared with the months left to the date it states itself. A ratio of 2× means it needs twice the time it says it has.</p>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "220px" }} /></div>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.project_code}`)} height="560px" />
    </div>
  );
}
```

- [ ] **Step 3: Field Audit**

`web/src/screens/Fields.tsx`:
```tsx
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num, share } from "../lib/format";

export function Fields() {
  const { bundle } = useBundle();
  const fa = bundle!.findings.field_audit;
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 24, bottom: 28 }, tooltip: {}, legend: { top: 0 },
    xAxis: { type: "category", data: fa.terminal_digit.map((d) => String(d.digit)), name: "last digit of reported progress" },
    yAxis: { type: "value", name: "share" },
    series: [
      { name: "reported", type: "bar", data: fa.terminal_digit.map((d) => d.share), color: "#1F5FA8" },
      { name: "if measured (uniform)", type: "line", data: fa.terminal_digit.map(() => 0.1), color: "#4B5A6B", lineStyle: { type: "dashed" }, showSymbol: false },
    ],
  }, [fa]);
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-semibold">Field Audit · what the form actually captures</h1>
      <p className="max-w-3xl text-sm text-muted">A genuinely measured percentage spreads its last digit evenly. Round-number clustering means the field is estimated, not measured. This is the supply-side answer to dimension (c): which fields carry information as filled.</p>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Whole numbers</div><div className="num text-2xl">{share(fa.whole_number_share)}</div><div className="text-xs text-muted">expected ≈ 1% if measured</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 5</div><div className="num text-2xl">{share(fa.multiple_of_5_share)}</div><div className="text-xs text-muted">expected ≈ 20% of whole numbers</div></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Multiples of 10</div><div className="num text-2xl">{share(fa.multiple_of_10_share)}</div><div className="text-xs text-muted">expected ≈ 10% of whole numbers</div></div>
      </div>
      <div className="rounded border border-line bg-surface p-3"><div ref={ref} style={{ height: "260px" }} /></div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-muted">Expenditure never updated across the reports, by agency (agencies with ≥5 projects)</div>
        {fa.staleness_by_agency.length === 0 && <div className="text-sm text-muted">No agency has five or more projects in this panel.</div>}
        <table className="w-full text-sm"><tbody>{fa.staleness_by_agency.slice(0, 15).map((a) => <tr key={a.agency_raw} className="border-t border-line"><td>{a.agency_raw}</td><td className="num text-right">{num(a.projects)} projects</td><td className="num text-right">{share(a.share_unchanged)} unchanged</td></tr>)}</tbody></table>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Predictions**

`web/src/screens/Predict.tsx`:
```tsx
import type { ColumnDef } from "@tanstack/react-table";
import { useNavigate } from "react-router-dom";
import { Badge } from "../components/Badge";
import { DataTable } from "../components/DataTable";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { bandClass, num, share } from "../lib/format";

const NAME: Record<string, string> = { LR_A: "Logistic regression · set A (conventional)", HGB_A: "Gradient boosting · set A", HGB_B: "Gradient boosting · set B (+ audit features)", HGB_B_SHUFFLED: "Control: labels shuffled" };
const COLOR: Record<string, string> = { LR_A: "#4B5A6B", HGB_A: "#8DA6C7", HGB_B: "#5B4B9A", HGB_B_SHUFFLED: "#D5DCE4" };

interface WRow { code: string; name: string; prob: number; rank: number; factor: string; band: string; delay: number | null; page: number }

export function Predict() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const m = bundle!.models;
  if (!m) return <div className="rounded border border-line bg-surface p-6 text-muted">models.json is not present. Run findings/run.py without --no-models.</div>;
  const test = m.meta.test_pair;
  const res = m.m1_slip.results.filter((r) => r.test_pair === test);
  const pair = m.meta.pairs.find((p) => p.id === test);
  const prRef = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 32 }, legend: { top: 0, textStyle: { fontSize: 10 } }, tooltip: { trigger: "item" },
    xAxis: { type: "value", name: "recall", min: 0, max: 1 }, yAxis: { type: "value", name: "precision", min: 0, max: 1 },
    series: res.map((r) => ({ name: NAME[r.model_id] ?? r.model_id, type: "line" as const, showSymbol: false, color: COLOR[r.model_id], data: r.pr_curve.map((p) => [p.x, p.y]) })),
  }, [test]);
  const hb = res.find((r) => r.model_id === "HGB_B");
  const calRef = useEChart({
    grid: { left: 48, right: 16, top: 16, bottom: 32 }, tooltip: {},
    xAxis: { type: "value", name: "predicted", min: 0, max: 1 }, yAxis: { type: "value", name: "observed", min: 0, max: 1 },
    series: [{ type: "line", data: [[0, 0], [1, 1]], lineStyle: { type: "dashed" }, color: "#D5DCE4", showSymbol: false },
      { type: "scatter", color: "#5B4B9A", data: (hb?.calibration ?? []).filter((c) => c.mean_pred != null).map((c) => [c.mean_pred, c.mean_obs, c.n]), symbolSize: (d: number[]) => Math.min(30, 4 + Math.sqrt(d[2])) }],
  }, [test]);
  const rows: WRow[] = m.m1_slip.watchlist.map((w) => {
    const p = bundle!.byCode.get(w.project_code)!;
    return { code: w.project_code, name: p.project_name, prob: w.slip_prob, rank: w.slip_rank, factor: p.ml?.slip_top_factors[0]?.feature ?? "—", band: p.risk.band,
      delay: p.ml?.expected_delay_months ?? null, page: p.snapshots[p.snapshots.length - 1].page };
  });
  const columns: ColumnDef<WRow, unknown>[] = [
    { header: "Rank", accessorKey: "rank", cell: (c) => <span className="num">{c.getValue() as number}</span> },
    { header: "Project", accessorKey: "name", cell: (c) => <span><span className="num text-muted">{c.row.original.code}</span> {c.getValue() as string}</span> },
    { header: "Slip prob. (model)", accessorKey: "prob", cell: (c) => <span className="num text-model">{share(c.getValue() as number)}</span> },
    { header: "Top factor", accessorKey: "factor" },
    { header: "Rule band", accessorKey: "band", cell: (c) => <Badge text={c.getValue() as string} className={bandClass[c.getValue() as string]} /> },
    { header: "Expected delay (months)", accessorKey: "delay", cell: (c) => <span className="num">{c.getValue() == null ? "—" : num(c.getValue() as number)}</span> },
    { header: "Page", accessorKey: "page", cell: (c) => <span className="num">{c.getValue() as number}</span> },
  ];
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Predictions · will a revised completion date be filed next report?</h1>
      <p className="max-w-3xl text-sm text-muted">Trained on {m.meta.train_pairs.join(", ")}, tested on {test} ({pair?.from} → {pair?.to}), a report the models never saw. n = <span className="num">{num(pair?.n)}</span>, projects that filed = <span className="num">{num(pair?.positives)}</span>, exits excluded = <span className="num">{num(pair?.censored_exits)}</span>. The conventional method is shown even where it wins.</p>
      <div className="overflow-x-auto rounded border border-line bg-surface">
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase text-muted"><th className="px-3 py-2">Model</th><th className="px-3 py-2">PR-AUC</th><th className="px-3 py-2">ROC-AUC</th><th className="px-3 py-2">Precision@100</th><th className="px-3 py-2">Recall@100</th><th className="px-3 py-2">Lift@100</th></tr></thead>
          <tbody>{res.map((r) => <tr key={r.model_id} className="border-t border-line" style={{ color: r.model_id === "HGB_B_SHUFFLED" ? "#4B5A6B" : undefined }}>
            <td className="px-3 py-2">{NAME[r.model_id] ?? r.model_id}</td><td className="num px-3 py-2">{r.pr_auc.toFixed(3)}</td><td className="num px-3 py-2">{r.roc_auc == null ? "—" : r.roc_auc.toFixed(3)}</td>
            <td className="num px-3 py-2">{share(r.precision_at_100)}</td><td className="num px-3 py-2">{share(r.recall_at_100)}</td><td className="num px-3 py-2">{r.lift_at_100 == null ? "—" : `${r.lift_at_100.toFixed(1)}×`}</td></tr>)}</tbody>
        </table>
        <div className="px-3 py-2 text-xs text-muted">Base rate on the test pair: {share(res[0]?.base_rate)}. Set B adds audit-derived features (pace, unreachable ratio, prior filings, agency history); the difference between the two gradient-boosting rows is the part of predictive power not on the current form.</div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Precision–recall on the held-out pair</div><div ref={prRef} style={{ height: "280px" }} /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Calibration (gradient boosting, set B)</div><div ref={calRef} style={{ height: "280px" }} /></div>
      </div>
      <h2 className="text-lg font-semibold">Watchlist · the 100 projects to review this month</h2>
      <DataTable columns={columns} rows={rows} onRowClick={(r) => nav(`/project/${r.code}`)} height="600px" />
    </div>
  );
}
```

- [ ] **Step 5: Drivers & Benchmark**

`web/src/screens/Drivers.tsx`:
```tsx
import { useNavigate } from "react-router-dom";
import { useBundle } from "../data/store";
import { useEChart } from "../lib/echart";
import { num } from "../lib/format";

const FEAT: Record<string, string> = { log_cost_original: "log(original cost)", age_months: "months since approval", physical_progress_pct: "physical progress %" };

function Pdp({ target }: { target: string }) {
  const { bundle } = useBundle();
  const pd = bundle!.models!.m3_drivers.partial_dependence.filter((p) => p.target === target);
  const ref = useEChart({
    grid: { left: 48, right: 16, top: 32, bottom: 32 }, legend: { top: 0, textStyle: { fontSize: 10 } }, tooltip: { trigger: "axis" },
    xAxis: { type: "value", name: "feature value (each series on its own scale, normalised 0–1)" }, yAxis: { type: "value", name: target === "cost_overrun_pct" ? "expected overrun %" : "expected months" },
    series: pd.map((p) => { const lo = Math.min(...p.grid), hi = Math.max(...p.grid) || 1; return { name: FEAT[p.feature] ?? p.feature, type: "line" as const, showSymbol: false, data: p.grid.map((g, i) => [(g - lo) / (hi - lo || 1), p.values[i]]) }; }),
  }, [target]);
  return <div ref={ref} style={{ height: "260px" }} />;
}

export function Drivers() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const m = bundle!.models;
  if (!m) return <div className="rounded border border-line bg-surface p-6 text-muted">models.json is not present.</div>;
  const d = m.m3_drivers;
  const secRef = useEChart({
    grid: { left: "22%", right: 16, top: 16, bottom: 28 }, tooltip: {},
    yAxis: { type: "category", data: d.sector_effects.map((s) => s.sector) }, xAxis: { type: "value", name: "cost overrun effect (pct points, OLS)" },
    series: [{ type: "bar", data: d.sector_effects.map((s) => s.effect_cost_pct), color: "#1F5FA8" }],
  }, [d]);
  const pts = bundle!.projects.filter((p) => p.ml?.peer_expected_cost_overrun_pct != null).map((p) => {
    const last = p.snapshots[p.snapshots.length - 1];
    const actual = last.cost_original_cr && last.cost_revised_cr != null ? ((last.cost_revised_cr - last.cost_original_cr) / last.cost_original_cr) * 100 : null;
    return { code: p.project_code, x: p.ml!.peer_expected_cost_overrun_pct as number, y: actual };
  }).filter((p) => p.y != null);
  const lim = Math.max(1, ...pts.map((p) => Math.max(p.x, p.y as number)));
  const scRef = useEChart({
    grid: { left: 56, right: 16, top: 16, bottom: 36 }, tooltip: { formatter: (q: { data: number[] }) => `expected ${q.data[0].toFixed(0)}% · actual ${q.data[1].toFixed(0)}%` },
    xAxis: { type: "value", name: "expected overrun % (peers)" }, yAxis: { type: "value", name: "actual overrun %" },
    series: [{ type: "scatter", symbolSize: 5, color: "#5B4B9A", data: pts.map((p) => [p.x, p.y, p.code]) }, { type: "line", data: [[0, 0], [lim, lim]], showSymbol: false, lineStyle: { type: "dashed" }, color: "#D5DCE4" }],
  }, [pts.length]);
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Drivers & Benchmark · what moves overrun across the panel</h1>
      <p className="max-w-3xl text-sm text-muted">Cross-sectional models on the {d.snapshot} report (n = <span className="num">{num(d.n)}</span>): ordinary least squares, the method of the published literature, beside gradient boosting. Five-fold cross-validation; this is a driver analysis, not a forecast.</p>
      <div className="overflow-x-auto rounded border border-line bg-surface"><table className="w-full text-sm">
        <thead><tr className="text-left text-xs uppercase text-muted"><th className="px-3 py-2">Target</th><th className="px-3 py-2">Model</th><th className="px-3 py-2">CV R²</th><th className="px-3 py-2">CV MAE</th></tr></thead>
        <tbody>{d.results.map((r, i) => <tr key={i} className="border-t border-line"><td className="px-3 py-2">{r.target === "cost_overrun_pct" ? "Cost overrun %" : "Time overrun (months)"}</td><td className="px-3 py-2">{r.model_id === "OLS" ? "OLS (conventional)" : "Gradient boosting"}</td><td className="num px-3 py-2">{r.cv_r2.toFixed(3)}</td><td className="num px-3 py-2">{r.cv_mae.toFixed(1)}</td></tr>)}</tbody></table></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Partial dependence · cost overrun %</div><Pdp target="cost_overrun_pct" /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Partial dependence · time overrun (months)</div><Pdp target="time_overrun_months" /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Sector effects (OLS coefficients)</div><div ref={secRef} style={{ height: "280px" }} /></div>
        <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Each project vs its peers (click a point in the table below to open)</div><div ref={scRef} style={{ height: "280px" }} /></div>
      </div>
      <div className="rounded border border-line bg-surface p-3">
        <div className="mb-2 text-xs uppercase text-muted">Worst residuals · overrun beyond what comparable projects show</div>
        <table className="w-full text-sm"><tbody>{bundle!.projects.filter((p) => p.ml?.cost_overrun_residual_pct != null).sort((a, b) => (b.ml!.cost_overrun_residual_pct as number) - (a.ml!.cost_overrun_residual_pct as number)).slice(0, 15).map((p) => (
          <tr key={p.project_code} className="cursor-pointer border-t border-line hover:bg-ground" onClick={() => nav(`/project/${p.project_code}`)}>
            <td className="num text-muted">{p.project_code}</td><td>{p.project_name}</td><td className="num text-right text-critical">+{(p.ml!.cost_overrun_residual_pct as number).toFixed(0)} pts</td></tr>))}</tbody></table>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Wire the routes, build, commit**

In `web/src/App.tsx` import `Exits`, `Warning`, `Fields`, `Predict`, `Drivers` from `./screens/...` and replace the five placeholder routes.

Run: `npm run build` then `python tools/validate.py` → green. Run `npm run dev` and open each of the five routes; every chart draws and every table sorts.

```powershell
git switch -c task/17-analysis-screens
git add -A
git commit -m "task 17: exits, early warning, field audit, predictions and drivers screens"
git push -u origin task/17-analysis-screens
gh pr create --title "Task 17: analysis screens" --body "<paste outputs>"
```

---

### Task 18: Assistant, Model Card, India map, review-pack export, demo runner, committed build

**Files:**
- Create: `web/src/screens/Assistant.tsx`, `web/src/screens/ModelCard.tsx`, `web/src/components/IndiaMap.tsx`, `web/src/components/ExportButton.tsx`, `web/src/assets/india_states.geojson` (downloaded), `RUN_DEMO.bat`, `web/dist/**` (built, committed)
- Modify: `web/src/App.tsx` (two routes), `web/src/screens/Overview.tsx` (map + export), `web/src/components/Layout.tsx` (export slot already exists)

**Interfaces:**
- Consumes: everything above; `findings.assistant`, `findings.review_pack`, `findings.by_state`, `modelCard.sections`.
- Produces: the last two routes; `RUN_DEMO.bat` that serves `web/dist` on port 8080 with Python only.

- [ ] **Step 1: The map data (one-time download, then offline forever)**

Run (PowerShell, in `web/`):
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/datameet/maps/master/States/Admin2.geojson" -OutFile src/assets/india_states.geojson
node -e "const g=require('./src/assets/india_states.geojson');console.log(g.features.length,'features; props:',Object.keys(g.features[0].properties));console.log([...new Set(g.features.map(f=>Object.values(f.properties)[0]))].sort().join(' | '))"
```
Expected: about 36 features and a property key that carries the state name (in DataMeet's file it is `ST_NM`). The printed name list must include `Ladakh`. If the URL 404s, open https://github.com/datameet/maps/tree/master/States and pick the states GeoJSON present there; the license is CC BY 4.0 — add the line `Map: DataMeet India maps (CC BY 4.0)` to the Model Card screen footer (Step 4). Set `NAME_PROP` in the component below to the key you saw.

- [ ] **Step 2: IndiaMap and ExportButton**

`web/src/components/IndiaMap.tsx`:
```tsx
import * as echarts from "echarts";
import { useEffect, useRef } from "react";
import geo from "../assets/india_states.geojson";
import { useBundle } from "../data/store";

const NAME_PROP = "ST_NM";
const norm = (s: string) => s.toLowerCase().replace(/&/g, "and").replace(/[^a-z]/g, "");
let registered = false;

export function IndiaMap() {
  const { bundle } = useBundle();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current || !bundle) return;
    const g = geo as unknown as { features: { properties: Record<string, string> }[] };
    if (!registered) { echarts.registerMap("india", geo as never); registered = true; }
    const names = new Map(g.features.map((f) => [norm(f.properties[NAME_PROP]), f.properties[NAME_PROP]]));
    const unmatched: string[] = [];
    const data = bundle.findings.by_state.map((s) => { const n = names.get(norm(s.key)); if (!n) unmatched.push(s.key); return { name: n ?? s.key, value: s.flagged, projects: s.projects }; });
    if (unmatched.length) console.warn("states not matched to map:", unmatched);
    const chart = echarts.init(ref.current);
    const max = Math.max(1, ...data.map((d) => d.value));
    chart.setOption({
      tooltip: { formatter: (p: { name: string; data?: { value: number; projects: number } }) => `${p.name}<br/>${p.data?.value ?? 0} flagged of ${p.data?.projects ?? 0} projects` },
      visualMap: { min: 0, max, left: 0, bottom: 0, text: ["flagged", ""], inRange: { color: ["#EAF0F6", "#1F5FA8", "#B42318"] }, calculable: false },
      series: [{ type: "map", map: "india", roam: false, data, itemStyle: { borderColor: "#FFFFFF" }, emphasis: { label: { show: true, fontSize: 10 } } }],
    });
    const onResize = () => chart.resize();
    window.addEventListener("resize", onResize);
    return () => { window.removeEventListener("resize", onResize); chart.dispose(); };
  }, [bundle]);
  return <div ref={ref} style={{ height: "420px" }} />;
}
```
(Add `declare module "*.geojson" { const v: unknown; export default v; }` to `web/src/vite-env.d.ts` so TypeScript accepts the import; Vite bundles `.geojson` as JSON when the file is imported with `?raw`-free syntax only if `assetsInclude` knows it — instead rename the file to `india_states.geo.json` and import `../assets/india_states.geo.json`, which Vite treats as JSON natively. Use the `.geo.json` name everywhere.)

`web/src/components/ExportButton.tsx`:
```tsx
import { useBundle } from "../data/store";

export function ExportButton() {
  const { bundle } = useBundle();
  const onClick = () => {
    const rows = bundle!.findings.review_pack;
    const cols = ["project_code", "project_name", "state", "sector", "risk_band", "risk_score", "slip_prob", "expected_delay_months", "flag_types", "page"] as const;
    const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = `agrim-review-pack-${bundle!.findings.meta.snapshots.at(-1)}.csv`; a.click();
    URL.revokeObjectURL(url);
  };
  return <button onClick={onClick} className="rounded bg-accent px-3 py-1 text-sm text-white hover:opacity-90">Export review pack (CSV)</button>;
}
```

In `web/src/components/Layout.tsx`, replace `<div id="header-actions" className="flex items-center gap-2" />` with `{bundle && <ExportButton />}` and add `import { ExportButton } from "./ExportButton";`.

In `web/src/screens/Overview.tsx`, replace `<div id="overview-map" />` with:
```tsx
<div className="grid gap-4 lg:grid-cols-2">
  <div className="rounded border border-line bg-surface p-3"><div className="text-xs uppercase text-muted">Flagged projects by state</div><IndiaMap /></div>
  <div className="rounded border border-line bg-surface p-3 text-sm">
    <div className="mb-2 text-xs uppercase text-muted">By sector</div>
    <table className="w-full"><tbody>{bundle!.findings.by_sector.slice().sort((a, b) => b.flagged - a.flagged).map((g) => <tr key={g.key} className="border-t border-line"><td>{g.key}</td><td className="num text-right">{num(g.flagged)} / {num(g.projects)} flagged</td><td className="num text-right text-critical">{num(g.red)} red</td></tr>)}</tbody></table>
  </div>
</div>
```
and add `import { IndiaMap } from "../components/IndiaMap";`.

- [ ] **Step 3: Assistant**

`web/src/screens/Assistant.tsx`:
```tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useBundle } from "../data/store";

const OLLAMA = "http://localhost:11434";

export function Assistant() {
  const { bundle } = useBundle();
  const nav = useNavigate();
  const [sel, setSel] = useState(0);
  const [code, setCode] = useState("");
  const [live, setLive] = useState(false);
  const [q, setQ] = useState("");
  const [a, setA] = useState<string | null>(null);
  useEffect(() => { fetch(`${OLLAMA}/`).then((r) => r.text()).then((t) => setLive(t.includes("Ollama is running"))).catch(() => setLive(false)); }, []);
  const qa = bundle!.findings.assistant;
  const ask = async () => {
    const p = bundle!.byCode.get(code.trim());
    const facts = p ? JSON.stringify({ project: p.project_name, code: p.project_code, snapshots: p.snapshots, flags: p.flags.map((f) => f.detail), risk: p.risk, ml: p.ml }) : "No project selected; answer only from general knowledge of the ledger structure.";
    setA("…");
    try {
      const r = await fetch(`${OLLAMA}/api/generate`, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: bundle!.briefs?.[0]?.model ?? "qwen2.5:3b", stream: false, options: { seed: 0, temperature: 0 },
          prompt: `You answer a monitoring officer using ONLY these facts. Do not invent numbers.\nFACTS: ${facts}\nQUESTION: ${q}\nANSWER:` }) });
      const j = await r.json();
      setA(j.response ?? "(no answer)");
    } catch (e) { setA(`Local model unavailable: ${(e as Error).message}`); }
  };
  return (
    <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
      <div className="space-y-2">
        <div className="rounded border border-line bg-surface p-3">
          <label className="text-xs uppercase text-muted">Open a project by code</label>
          <div className="mt-1 flex gap-2"><input value={code} onChange={(e) => setCode(e.target.value)} className="num w-full rounded border border-line px-2 py-1" placeholder="e.g. 705526" />
            <button className="rounded bg-accent px-3 text-sm text-white" onClick={() => bundle!.byCode.has(code.trim()) && nav(`/project/${code.trim()}`)}>Open</button></div>
          {code && !bundle!.byCode.has(code.trim()) && <div className="mt-1 text-xs text-critical">No project with that code in the parsed reports.</div>}
        </div>
        <div className="rounded border border-line bg-surface">
          {qa.map((x, i) => <button key={x.id} onClick={() => setSel(i)} className={`block w-full border-b border-line px-3 py-2 text-left text-sm last:border-b-0 ${sel === i ? "bg-ground font-medium" : ""}`}>{x.question}</button>)}
        </div>
      </div>
      <div className="space-y-4">
        <div className="rounded border border-line bg-surface p-4">
          <div className="text-xs uppercase text-muted">Answer · from the ledger, deterministic</div>
          <p className="mt-2 text-sm">{qa[sel]?.answer}</p>
          {qa[sel]?.sources.length > 0 && <div className="mt-2 flex flex-wrap gap-1">{qa[sel].sources.map((s, i) => <span key={i} className="num rounded border border-line px-1 text-xs text-muted">{s.snapshot} p.{s.page}</span>)}</div>}
        </div>
        {live ? (
          <div className="rounded border border-model bg-surface p-4">
            <div className="text-xs uppercase text-model">Ask the local model (Ollama detected) · grounded on the project you typed above</div>
            <textarea value={q} onChange={(e) => setQ(e.target.value)} className="mt-2 w-full rounded border border-line p-2 text-sm" rows={3} placeholder="Why does this project look risky?" />
            <button onClick={ask} className="mt-2 rounded bg-model px-3 py-1 text-sm text-white">Ask</button>
            {a && <p className="mt-2 text-sm">{a}</p>}
          </div>
        ) : <div className="text-xs text-muted">Live model mode is off (no local Ollama detected). Every answer above is computed from the ledger and cannot hallucinate.</div>}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Model Card**

`web/src/screens/ModelCard.tsx`:
```tsx
import { useBundle } from "../data/store";

export function ModelCard() {
  const { bundle } = useBundle();
  const mc = bundle!.modelCard;
  if (!mc) return <div className="rounded border border-line bg-surface p-6 text-muted">model_card.json is not present.</div>;
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-xl font-semibold">Model Card · generated {mc.generated_at}</h1>
      {mc.sections.map((s) => (
        <section key={s.title} className="rounded border border-line bg-surface p-4">
          <h2 className="mb-2 font-semibold">{s.title}</h2>
          <ul className="list-disc space-y-1 pl-5 text-sm">{s.lines.map((l, i) => <li key={i}>{l}</li>)}</ul>
        </section>
      ))}
      <p className="text-xs text-muted">Source data: MoSPI Flash Reports (public). Map: DataMeet India maps (CC BY 4.0). Stack: Python, pdfplumber, scikit-learn, SHAP, Ollama, React, ECharts. All open source.</p>
    </div>
  );
}
```

Wire `Assistant` and `ModelCard` routes in `App.tsx`.

- [ ] **Step 5: Demo runner and the committed build**

`RUN_DEMO.bat` at the repo root:
```bat
@echo off
cd /d %~dp0
if not exist web\dist\index.html (
  echo web\dist is missing. Run: cd web ^&^& npm run build
  pause
  exit /b 1
)
start "" http://localhost:8080/
python -m http.server 8080 -d web\dist
```

Run (in `web/`): `npm run build`. Then from the root: `RUN_DEMO.bat`. Expected: browser opens `http://localhost:8080/`, the app loads with Wi-Fi off (switch it off to check), every route works, a source page image opens, the CSV export downloads. Press Ctrl+C in the server window.

Run: `python tools/validate.py` → PASS.

- [ ] **Step 6: Commit (including `web/dist`)**

```powershell
git switch -c task/18-assistant-map-demo
git add -A
git commit -m "task 18: assistant, model card, India map, review-pack export, RUN_DEMO.bat, committed build"
git push -u origin task/18-assistant-map-demo
gh pr create --title "Task 18: assistant, map, export, demo runner" --body "<paste outputs; state that the Wi-Fi-off run was done>"
```

---

### Task 19: LLM project briefs with a grounding check (offline, cached)

**Files:**
- Create: `findings/briefs.py`, `web/public/data/briefs.json` (generated, committed)
- Test: `tests/findings/test_briefs.py`

**Interfaces:**
- Consumes: `web/public/data/projects.json`, `findings.json`; a local Ollama with `qwen2.5:3b` pulled (only on the machine that runs this task).
- Produces: `findings.briefs.fact_sheet(project: dict) -> str`, `findings.briefs.numbers_in(text: str) -> set[str]`, `findings.briefs.grounded(brief: str, facts: str) -> bool`, `findings.briefs.template_brief(project) -> str`, CLI `python -m findings.briefs [--top 60] [--codes 705526,...]` writing `briefs.json` matching `briefs.schema.json`.

- [ ] **Step 0: Human prerequisite (P's laptop, ≥ 8 GB RAM)**

Install Ollama from https://ollama.com (Windows installer), then run `ollama pull qwen2.5:3b` (about 2 GB). Check: `curl http://localhost:11434/` prints `Ollama is running`. If Ollama cannot be installed on any team laptop, skip to Step 5 with `--template-only`: the briefs file is still produced from templates with `grounded: false` and `model: "template"`, and the pitch says so.

- [ ] **Step 1: Write the failing tests (no Ollama needed)**

Create `tests/findings/test_briefs.py`:
```python
import json

from findings.briefs import fact_sheet, grounded, numbers_in, template_brief

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
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/findings/test_briefs.py -q` → import error.

- [ ] **Step 3: Write `findings/briefs.py`**

```python
"""LLM project briefs, generated ONCE at build time from a fact sheet, verified number-by-number, cached to briefs.json.
Usage: python -m findings.briefs [--top 60] [--codes 705526,612793] [--model qwen2.5:3b] [--template-only]"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web" / "public" / "data"
SEED = 0
NUM = re.compile(r"\d[\d,]*\.?\d*")
SYSTEM = ("You write a four-sentence brief for a government infrastructure monitoring officer. Use only the facts below. "
          "Do not introduce any number that is not in the facts. Plain English, no headings, no bullet points.")


def numbers_in(text):
    out = set()
    for m in NUM.findall(text or ""):
        t = m.replace(",", "").rstrip(".")
        if t:
            out.add(t.rstrip("0").rstrip(".") if "." in t else t)
    return out


def _n(x):
    return "—" if x is None else (f"{x:,.2f}" if isinstance(x, float) else str(x))


def fact_sheet(p):
    lines = [f"Project {p['project_code']}: {p['project_name']}; agency {p['agency_raw'] or 'not printed'}; state {p['state'] or 'not printed'}; sector {p['sector'] or 'unknown'}.",
             f"Seen from {p['first_seen']} to {p['last_seen']}; status {p['status']}."]
    for s in p["snapshots"]:
        lines.append(f"Report {s['snapshot']} (page {s['page']}): progress {_n(s['physical_progress_pct'])}%, cumulative expenditure {_n(s['expenditure_cum_cr'])} crore, "
                     f"original cost {_n(s['cost_original_cr'])} crore, revised cost {_n(s['cost_revised_cr'])} crore, original completion {s['doc_original'] or 'not printed'}, revised completion {s['doc_revised'] or 'none'}.")
    for f in p["flags"]:
        lines.append(f"Flag ({f['severity']}): {f['detail']}")
    lines.append(f"Rule-based risk score {p['risk']['score']} ({p['risk']['band']}).")
    ml = p.get("ml")
    if ml:
        if ml.get("slip_prob") is not None:
            lines.append(f"Model: probability of a revised completion date being filed next report {round(100 * ml['slip_prob'])} percent, rank {ml['slip_rank']}.")
        if ml.get("expected_completion"):
            lines.append(f"Model: expected completion {ml['expected_completion']}, expected delay {_n(ml['expected_delay_months'])} months versus the stated date.")
        if ml.get("cost_overrun_residual_pct") is not None:
            lines.append(f"Model: cost overrun {_n(ml['cost_overrun_residual_pct'])} percentage points above comparable projects.")
    return "\n".join(lines)


def grounded(brief, facts):
    return numbers_in(brief) <= numbers_in(facts)


def template_brief(p):
    last = p["snapshots"][-1]
    first = p["flags"][0]["detail"] if p["flags"] else "No contradictions were found in its record."
    return (f"{p['project_name']} ({p['project_code']}) is monitored under {p['agency_raw'] or 'an unnamed agency'} in {p['state'] or 'an unstated location'}. "
            f"In the {last['snapshot']} report it stands at {_n(last['physical_progress_pct'])}% physical progress with cumulative expenditure of {_n(last['expenditure_cum_cr'])} crore against a revised cost of {_n(last['cost_revised_cr'])} crore. "
            f"{first} "
            f"The rule-based risk score is {p['risk']['score']} ({p['risk']['band']}).")


def _ollama_generate(model, prompt):
    import ollama
    r = ollama.generate(model=model, prompt=prompt, options={"seed": SEED, "temperature": 0, "num_ctx": 4096}, stream=False)
    return (r.get("response") or "").strip()


def brief_for(p, model, template_only=False):
    facts = fact_sheet(p)
    h = hashlib.sha256(facts.encode("utf-8")).hexdigest()
    if template_only:
        return {"project_code": p["project_code"], "brief": template_brief(p), "model": "template", "seed": SEED,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": True, "attempts": 0, "facts_hash": h}
    prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nBRIEF:"
    attempts, text = 0, ""
    for attempts in range(1, 4):
        text = _ollama_generate(model, prompt)
        if text and grounded(text, facts):
            return {"project_code": p["project_code"], "brief": text, "model": model, "seed": SEED,
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": True, "attempts": attempts, "facts_hash": h}
        bad = sorted(numbers_in(text) - numbers_in(facts))
        prompt = f"{SYSTEM}\n\nFACTS:\n{facts}\n\nYour previous brief contained numbers not in the facts: {', '.join(bad)}. Remove them and write the brief again.\n\nBRIEF:"
    return {"project_code": p["project_code"], "brief": template_brief(p), "model": model, "seed": SEED,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "grounded": False, "attempts": attempts, "facts_hash": h}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--codes", default="")
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--template-only", action="store_true")
    a = ap.parse_args(argv)
    projects = json.loads((DATA / "projects.json").read_text(encoding="utf-8"))
    ongoing = sorted((p for p in projects if p["status"] == "ongoing"), key=lambda p: (-p["risk"]["score"], p["project_code"]))
    wanted = [p["project_code"] for p in ongoing[:a.top]] + [c.strip() for c in a.codes.split(",") if c.strip()]
    by = {p["project_code"]: p for p in projects}
    out_path = DATA / "briefs.json"
    existing = {b["project_code"]: b for b in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}
    out = []
    for code in dict.fromkeys(wanted):
        p = by.get(code)
        if not p:
            print("skip unknown code", code)
            continue
        h = hashlib.sha256(fact_sheet(p).encode("utf-8")).hexdigest()
        if code in existing and existing[code]["facts_hash"] == h and existing[code]["grounded"]:
            out.append(existing[code])
            continue
        b = brief_for(p, a.model, a.template_only)
        print(code, "grounded" if b["grounded"] else "TEMPLATE FALLBACK", f"(attempts {b['attempts']})")
        out.append(b)
    out.sort(key=lambda b: b["project_code"])
    out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}: {len(out)} briefs, {sum(b['grounded'] for b in out)} grounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests**

Run: `pytest tests/findings/test_briefs.py -q` → 3 passed.

- [ ] **Step 5: Generate the briefs**

Run (with Ollama running): `python -m findings.briefs --top 60 --codes <opener_code from deck/numbers.json>`
Expected: sixty-plus lines ending `grounded` or `TEMPLATE FALLBACK`, then `wrote ...briefs.json: N briefs, M grounded`. Ten minutes or so on CPU. Without Ollama: add `--template-only` to the same command.

Run: `python tools/validate.py` → `ok   briefs: valid`, `RESULT: PASS`. Open `#/project/<opener_code>` (after `npm run build` in `web/`): the brief card shows the verified chip.

- [ ] **Step 6: Commit**

```powershell
cd web; npm run build; cd ..
git switch -c task/19-briefs
git add -A
git commit -m "task 19: offline LLM briefs with number-level grounding check; cached briefs.json"
git push -u origin task/19-briefs
gh pr create --title "Task 19: LLM briefs" --body "<paste the last line of the briefs run and validate output>"
```

---

### Task 20: Deck, pitch, rehearsal, release tag

**Files:**
- Create: `tools/slides.py`, `deck/slides.md` (generated), `deck/pitch.md`, `deck/AGRIM-SIH26103.pptx` (filled by hand in the official template), `deck/AGRIM-SIH26103.pdf` (exported)
- Test: `tests/tools/test_slides.py`; `python tools/validate.py` (checks `deck/numbers.json` traceability and `deck/pitch.md` for hardcoded numbers)

**Interfaces:**
- Consumes: `deck/numbers.json`, `web/public/data/findings.json`, `models.json`.
- Produces: `deck/slides.md` — the exact text for each of the six template slides with every number substituted from `numbers.json`; the pitch script with timings; the tagged release `v0.1-internal-round`.

- [ ] **Step 1: Write the failing test**

Create `tests/tools/test_slides.py`:
```python
import json
from pathlib import Path

import pytest

from tools.slides import render

NUMS = Path("deck/numbers.json")


@pytest.mark.skipif(not NUMS.exists(), reason="deck/numbers.json not generated")
def test_slides_render_all_six_and_use_only_known_numbers():
    nums = json.loads(NUMS.read_text(encoding="utf-8"))
    text = render(nums)
    for heading in ["TITLE PAGE", "IDEA TITLE", "TECHNICAL APPROACH", "FEASIBILITY AND VIABILITY", "IMPACT AND BENEFITS", "RESEARCH AND REFERENCES"]:
        assert heading in text
    assert "{" not in text and "}" not in text            # every placeholder substituted
    assert str(nums["projects_latest"]) in text
```

- [ ] **Step 2: Write `tools/slides.py`**

```python
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
```

Run: `python tools/slides.py` then `pytest tests/tools/test_slides.py -q`. If the test reports a leftover `{...}`, a key is missing from `deck/numbers.json`: add it to `deck_numbers()` in `findings/run.py` (Task 9) only if it is a real number in the JSON; otherwise reword the slide. Re-run `python -m findings.run --panel data/out/panel.csv --out web/public/data --deck deck/numbers.json` after any such change.

- [ ] **Step 3: Fill the official template by hand**

Download https://www.sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx to `deck/AGRIM-SIH26103.pptx`. For each slide, paste the bullets from `deck/slides.md` into the template's existing text boxes without changing the headings or pointer text; delete slide 7 ("IMPORTANT INSTRUCTIONS"); keep six slides. On slide 3 draw the flow as boxes and arrows (the template allows diagrams). Add one screenshot of the Contradiction Ledger and the comparison table from Predictions on slide 4 (not a gallery of UI). Export as PDF to `deck/AGRIM-SIH26103.pdf`.

- [ ] **Step 4: Write the pitch**

Create `deck/pitch.md` (numbers are written as `{key}` placeholders read aloud from `deck/slides.md`; the validator forbids typed numbers here):
```markdown
# AGRIM — 3-minute pitch (one presenter; operator drives the demo silently)

## 0:00–0:20 — The fact
"In the Ministry's own April report, one project reports fifty-three thousand crore spent. In the next report, four hundred crore. Progress went up. Nobody flagged it. We found {contradictions_total} more like it across the reports."
(Operator: `#/ledger?type=EXP_DECREASE`, then `#/project/{opener_code}`, then Source page. The spoken figures are `opener_before_cr` and `opener_after_cr` from `deck/slides.md`, said in words.)

## 0:20–1:35 — The demo
- Ledger → project page → source PDF page ("their own PDF").
- Outlook card: "and the model's view, with its five reasons."
- `#/predict`: "We trained on December to June and tested on July, a report the model never saw. Gradient boosting against logistic regression, side by side. The audit features added this much."
- `#/exits`: "{exits_total} projects left the panel. The report prints how many were commissioned."
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
Why this PS · How is this different from an AI dashboard · Isn't a revised date just paperwork · Where did the exited projects go · Does it need PAIMANA access · The CUF question (set A vs B) · What is your accuracy (we report PR-AUC and top-100 recall with positives) · Why not predict cost overrun (too few events) · Why HistGradientBoosting (same family, zero extra dependencies, native NaN, baseline in the same library) · Did you use an LLM (offline briefs, every number verified).
```

- [ ] **Step 5: Rehearse on a cold machine**

On a second laptop: `git clone <repo> C:\dev\agrim`, no `npm install`, no Python packages, Wi-Fi off, run `RUN_DEMO.bat`. Expected: the app loads and the whole demo path works from the committed `web/dist` and `web/public/data`. Time the pitch three times; record the times at the bottom of `deck/pitch.md` as `Rehearsal: <date> <m:ss>, <m:ss>, <m:ss>` (these are the only numbers allowed there, under two digits each).

- [ ] **Step 6: Gate, commit, tag**

Run: `python tools/validate.py` → PASS (checks `deck/numbers.json` traceability and `deck/pitch.md`).

```powershell
git switch -c task/20-deck-pitch
git add -A
git commit -m "task 20: slides rendered from numbers.json, official template filled, pitch, rehearsal"
git push -u origin task/20-deck-pitch
gh pr create --title "Task 20: deck and pitch" --body "<paste validate output and the three rehearsal times>"
```
After merge: `git switch main; git pull; git tag v0.1-internal-round; git push origin v0.1-internal-round`. Copy the repo folder to a USB stick.

---

## Self-review against `docs/BUILD.md` v2

**Spec coverage.** F1–F6 → Tasks 6–8; assistant, review pack, coverage, headline, by-state/by-sector → Task 9; feature sets A/B and the leakage rule → Task 10; M1 with LR baseline, shuffle control, SHAP, watchlist → Task 11; M2 with ZERO/OWN_VELOCITY baselines and outlook → Task 12; M3 OLS vs HGB, PDP, peer benchmark, M4 IsolationForest → Task 13; model card and `ml` blocks → Task 14; every screen in BUILD §8 → Tasks 15–18 (Overview with map, Ledger, Project with Outlook card and source page, Exits, Warning, Fields, Predict with comparison table and watchlist, Drivers, Assistant with live mode, Model Card); export and persona filter → Task 18; LLM briefs with grounding → Task 19; deck in the official template, pitch, cold rehearsal → Task 20; page images → Task 9; determinism, `OMP_NUM_THREADS=1`, committed outputs, `RUN_DEMO.bat` → Tasks 2, 9, 14, 18. Not covered on purpose (BUILD §1 "not built"): survival model, archive ingestion, WPI/IMD, NLP sector normalisation.

**Deviations from BUILD.md decisions, with reasons.** D16: shadcn/ui dropped in favour of Tailwind plus four small hand-written components (an interactive CLI and dozens of generated files are wrong for a relay with mixed tools). D20: Ajv validates the JSON Schema files directly in the browser and `json-schema-to-typescript` generates the types, instead of Zod (one schema file for both Python and TypeScript, no second hand-written schema to drift). TanStack Table is pinned to v8 (the API this plan's code uses). Tests live under `tests/` at the root rather than inside each component. Page images live under `web/public/pages/` so the static server can serve them. `web/dist` is committed so the demo laptop needs no Node. `data/aggregates.json` lives under `data/`, not `contracts/`, so no task outside 2 and 9 writes to `contracts/`.

**Type consistency checked.** `flags` dicts carry `project_code` internally and are stripped in `run.py`; `exits.compute` returns `status[code] = (status, first_seen, last_seen)` consumed by `build_projects`; `early_warning.compute` returns `{"rows", "flags"}`; `pair_frame` columns are `FEATURES_B + ["y_slip", "delta_prog", "prog_t1"]` in every model; `to_matrix` returns `(frames, mask)`; `m1_slip.run` returns `(m1, per_project, pairs_meta)`; `pipeline.run` returns `(models, ml, extra_flags, model_card)` and `run.py` unpacks exactly that.

**Known thin spots (say them, do not hide them).** Task 4's extraction regexes are written against the header text and one sample row; the real cell layout is confirmed only when Step 7 runs. Task 18's GeoJSON URL and the `ST_NM` property name are the best-known DataMeet paths and are checked by the command in Step 1. Ollama's browser CORS behaviour for the live assistant mode is unverified; the mode hides itself on any failure and is never on the demo path.
