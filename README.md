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
