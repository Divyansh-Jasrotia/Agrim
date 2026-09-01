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
