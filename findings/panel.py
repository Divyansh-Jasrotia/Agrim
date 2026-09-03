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
