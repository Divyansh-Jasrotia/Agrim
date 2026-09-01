"""Download the five Flash Report PDFs ONCE, verify sizes, write SHA256SUMS. The only network code in the parser side.
Run: python tools/fetch_pdfs.py            (downloads what is missing, then verifies)
     python tools/fetch_pdfs.py --verify   (verifies only)
"""
import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

M = "https://www.mospi.gov.in/uploads/publications_reports/"
PDFS = {
    "2025-12": ("FlashReport_December_2025.pdf", M + "publications_reports1769671627281_5812a634-546b-405d-921c-f84c4da453dc_FlashReport_December_2025.pdf", 6398361),
    "2026-04": ("Flash_Report_April_2026.pdf", M + "publications_reports1779688125413_332125c5-1fb9-4d23-87ca-dd89fc14cd15_Flash_Report_April_2026.pdf", 6543938),
    "2026-05": ("FlashReport_May_2026.pdf", M + "publications_reports1782388627305_2544b8eb-3ea2-40eb-ab6e-b150c40c4a9e_FlashReport_May_2026.pdf", 6460757),
    "2026-06": ("FlashReport_June_2026.pdf", M + "publications_reports1785229543014_f9b01e19-0a7a-4975-9276-34e02259c2e0_FlashReport_June_2026_.pdf", 6540236),
    "2026-07": ("FlashReport_July_2026.pdf", M + "publications_reports1787656864174_db1695c9-b038-4c20-964f-8cf5f2cdda5f_FlashReport_July_2026_.pdf", 6451056),
}
DIR = Path(__file__).resolve().parents[1] / "data" / "pdfs"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AGRIM fetch; student project)"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            out.write(chunk)


def write_sums(files, sums_path):
    lines = [f"{sha256(f)}  {Path(f).name}" for f in files]
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_sums(sums_path, directory):
    bad = []
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        f = Path(directory) / name
        if not f.exists() or sha256(f) != digest:
            bad.append(name)
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    DIR.mkdir(parents=True, exist_ok=True)
    sums = DIR / "SHA256SUMS"
    if not a.verify:
        for snap, (name, url, size) in PDFS.items():
            dest = DIR / name
            if dest.exists() and dest.stat().st_size == size:
                print("have", name)
                continue
            print("fetching", snap, "->", name)
            download(url, dest)
            got = dest.stat().st_size
            if got != size:
                print(f"WARNING size mismatch for {name}: expected {size}, got {got}. If the mirror re-uploaded the file, update PDFS.")
        write_sums([DIR / n for n, _, _ in PDFS.values()], sums)
        print("wrote", sums)
    bad = verify_sums(sums, DIR)
    print("verify:", "OK" if not bad else f"MISMATCH {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
