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
