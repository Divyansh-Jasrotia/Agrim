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
