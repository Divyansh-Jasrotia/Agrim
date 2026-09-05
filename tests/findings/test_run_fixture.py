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
