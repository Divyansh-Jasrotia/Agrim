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
