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
