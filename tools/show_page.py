"""Print the text (and optionally the extracted tables) of one PDF page, 1-based.
Run: python tools/show_page.py data/pdfs/Flash_Report_April_2026.pdf 3
     python tools/show_page.py data/pdfs/Flash_Report_April_2026.pdf 56 --tables
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber

path, page_no = sys.argv[1], int(sys.argv[2])
with pdfplumber.open(path) as pdf:
    page = pdf.pages[page_no - 1]
    print(page.extract_text() or "<no text layer>")
    if "--tables" in sys.argv:
        settings = {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 3, "join_tolerance": 3, "intersection_tolerance": 3}
        for t_i, table in enumerate(page.extract_tables(settings)):
            print(f"--- table {t_i}: {len(table)} rows")
            for row in table[:6]:
                print([(c or "").replace("\n", "\\n")[:40] for c in row])
