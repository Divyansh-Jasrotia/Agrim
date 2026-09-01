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
