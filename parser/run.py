"""CLI: python -m parser.run --snapshot 2026-04 [--peek 3]   -> data/out/parts/<snapshot>.csv
        python -m parser.run --merge                          -> data/out/panel.csv + data/out/parse_coverage.md"""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from parser.adapters import ADAPTERS
from parser.extract import extract_rows_with_totals
from parser.normalize import COLUMNS, normalize
from tools.fetch_pdfs import sha256

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "pdfs"
OUT = ROOT / "data" / "out"
SNAPSHOT_ORDER = ["2025-12", "2026-04", "2026-05", "2026-06", "2026-07"]


def aggregates():
    p = ROOT / "data" / "aggregates.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def parse_snapshot(snapshot, peek=0, with_totals=False):
    """with_totals=True also returns the declared-total accounting (list of N from each skipped
    "Total (N)" row) -- see extract_rows_with_totals. Default False keeps the return type a bare
    list of rows for existing callers (tests/parser/test_april_real.py)."""
    ad = ADAPTERS[snapshot]
    pdf = PDF_DIR / ad.file
    sha = sha256(pdf)
    raws, totals = extract_rows_with_totals(pdf, ad.pages)
    if peek:
        for r in raws[:peek]:
            print(f"page {r.page} section={r.section!r}")
            for c in r.cells:
                print("   ", repr(c))
    rows = [normalize(r, snapshot, ad.file, sha) for r in raws]
    return (rows, totals) if with_totals else rows


def write_rows(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})


def report(rows, snapshot, totals=None):
    """totals: the declared-N list from extract_rows_with_totals, when the caller has it (the
    per-snapshot --snapshot path). merge() reads parts CSVs back in and has no totals to pass, so
    this line is skipped there -- it is the per-parse completeness check, not a panel-wide one.
    """
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
    if totals is not None:
        declared, parsed = sum(totals), len(rows)
        print(f"  declared Total(N) sum = {declared} vs parsed = {parsed}")
        if declared != parsed:
            print(f"  WARNING: declared Total(N) sum ({declared}) != parsed rows ({parsed})")
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
        rows, totals = parse_snapshot(a.snapshot, a.peek, with_totals=True)
        write_rows(rows, OUT / "parts" / f"{a.snapshot}.csv")
        report(rows, a.snapshot, totals)
    if a.merge:
        merge()
    if not a.snapshot and not a.merge:
        ap.error("give --snapshot <YYYY-MM> and/or --merge")


if __name__ == "__main__":
    sys.exit(main())
