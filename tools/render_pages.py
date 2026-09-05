"""Render every PDF page cited by a non-info flag to web/public/pages/<snapshot>/p<page>.png (PyMuPDF, 1.5x zoom)."""
import json
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_pdfs import PDFS


def cited_pages(findings_path):
    f = json.loads(Path(findings_path).read_text(encoding="utf-8"))
    pages = set()
    for r in f["contradictions"]["rows"] + f["early_warning"]["rows"] + f["exits"]["rows"]:
        for s in r["sources"]:
            pages.add((s["snapshot"], s["page"]))
    return sorted(pages)


def render(pages, out_dir=ROOT / "web" / "public" / "pages"):
    docs = {}
    n = 0
    for snap, page in pages:
        pdf = ROOT / "data" / "pdfs" / PDFS[snap][0]
        if not pdf.exists():
            continue
        doc = docs.setdefault(snap, fitz.open(pdf))
        dest = out_dir / snap / f"p{page}.png"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(dest)
        n += 1
    return n


if __name__ == "__main__":
    pages = cited_pages(ROOT / "web" / "public" / "data" / "findings.json")
    print("cited pages:", len(pages), "rendered new:", render(pages))
